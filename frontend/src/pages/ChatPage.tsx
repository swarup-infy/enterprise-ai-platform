import {
  FileText,
  LayoutDashboard,
  LogOut,
  Menu,
  MessageSquare,
  Plus,
  Send,
  Sparkles,
  Trash2,
  User,
  X,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type FormEvent,
  type KeyboardEvent,
  type ReactNode,
} from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

import {
  deleteChatConversation,
  getChatConversation,
  getChatHistory,
  sendChatMessage,
  type ChatHistoryItem,
} from "../services/api";

import "./ChatPage.css";

/* ==========================================================================
   Types
   ========================================================================== */

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  time: string;
}

interface ChatResponseLike {
  answer?: string;
  response?: string;
  message?: string;
  conversation_id?: string | number;
  [key: string]: unknown;
}

type HistoryResponse =
  | ChatHistoryItem[]
  | ChatHistoryItem
  | null
  | undefined;

/* ==========================================================================
   Constants
   ========================================================================== */

const MAX_MESSAGE_LENGTH = 10_000;
const COLLECTION_NAME = "documents";
const TOP_K = 5;

const WELCOME_MESSAGE: ChatMessage = {
  id: "welcome",
  role: "assistant",
  content:
    "Hello! I'm your Enterprise AI assistant. Ask me anything about your uploaded documents.",
  time: "Now",
};

const SUGGESTIONS = [
  {
    icon: FileText,
    title: "Summarize my documents",
    text: "Give me a concise summary of my uploaded documents.",
  },
  {
    icon: Sparkles,
    title: "Find important points",
    text: "What are the most important points in my documents?",
  },
  {
    icon: MessageSquare,
    title: "Ask about a document",
    text: "What are the key findings from my latest document?",
  },
];

/* ==========================================================================
   Utilities
   ========================================================================== */

function getCurrentTime(): string {
  return new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatTime(value?: string): string {
  if (!value) {
    return "";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "";
  }

  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function normalizeHistory(
  response: HistoryResponse,
): ChatHistoryItem[] {
  if (Array.isArray(response)) {
    return response;
  }

  if (response) {
    return [response];
  }

  return [];
}

function getErrorMessage(error: unknown): string {
  if (
    typeof error === "object" &&
    error !== null &&
    "response" in error
  ) {
    const response = (
      error as {
        response?: {
          data?: {
            detail?: unknown;
          };
        };
      }
    ).response;

    const detail = response?.data?.detail;

    if (typeof detail === "string" && detail.trim()) {
      return detail;
    }

    if (Array.isArray(detail)) {
      const firstMessage = detail.find(
        (item) =>
          typeof item === "object" &&
          item !== null &&
          "msg" in item &&
          typeof (item as { msg?: unknown }).msg === "string",
      );

      if (
        firstMessage &&
        typeof (firstMessage as { msg: string }).msg === "string"
      ) {
        return (firstMessage as { msg: string }).msg;
      }

      return "The server rejected the chat request.";
    }
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  return "Unable to process your request. Please try again.";
}

function getConversationId(
  response: ChatResponseLike,
): string | null {
  const value = response.conversation_id;

  if (
    typeof value === "string" &&
    value.trim()
  ) {
    return value.trim();
  }

  if (
    typeof value === "number" &&
    Number.isFinite(value)
  ) {
    return String(value);
  }

  return null;
}

function createMessageId(
  prefix: string,
): string {
  if (
    typeof crypto !== "undefined" &&
    typeof crypto.randomUUID === "function"
  ) {
    return `${prefix}-${crypto.randomUUID()}`;
  }

  return `${prefix}-${Date.now()}-${Math.random()
    .toString(36)
    .slice(2)}`;
}

/* ==========================================================================
   AI Logo
   ========================================================================== */

function AiCatLogo({
  className = "",
}: {
  className?: string;
}) {
  return (
    <img
      src="/ai-cat.gif"
      alt="AI Assistant"
      className={`ai-cat-logo ${className}`}
    />
  );
}

/* ==========================================================================
   Markdown
   ========================================================================== */

function renderInlineMarkdown(
  text: string,
): ReactNode[] {
  const parts = text.split(
    /(\*\*[^*]+\*\*|__[^_]+__|`[^`]+`|\*[^*]+\*|_[^_]+_)/g,
  );

  return parts.map((part, index) => {
    if (!part) {
      return null;
    }

    if (
      part.startsWith("**") &&
      part.endsWith("**") &&
      part.length > 4
    ) {
      return (
        <strong key={index}>
          {part.slice(2, -2)}
        </strong>
      );
    }

    if (
      part.startsWith("__") &&
      part.endsWith("__") &&
      part.length > 4
    ) {
      return (
        <strong key={index}>
          {part.slice(2, -2)}
        </strong>
      );
    }

    if (
      part.startsWith("`") &&
      part.endsWith("`") &&
      part.length > 2
    ) {
      return (
        <code key={index}>
          {part.slice(1, -1)}
        </code>
      );
    }

    if (
      part.startsWith("*") &&
      part.endsWith("*") &&
      part.length > 2
    ) {
      return (
        <em key={index}>
          {part.slice(1, -1)}
        </em>
      );
    }

    if (
      part.startsWith("_") &&
      part.endsWith("_") &&
      part.length > 2
    ) {
      return (
        <em key={index}>
          {part.slice(1, -1)}
        </em>
      );
    }

    return (
      <span key={index}>
        {part}
      </span>
    );
  });
}

function MarkdownMessage({
  content,
}: {
  content: string;
}) {
  const normalizedContent = content
    .replace(/\r\n/g, "\n")
    .replace(/\r/g, "\n");

  const lines = normalizedContent.split("\n");

  const blocks: ReactNode[] = [];

  let paragraph: string[] = [];
  let bulletItems: string[] = [];
  let numberedItems: string[] = [];

  const flushParagraph = () => {
    if (paragraph.length === 0) {
      return;
    }

    const text = paragraph.join(" ").trim();

    if (text) {
      blocks.push(
        <p key={`paragraph-${blocks.length}`}>
          {renderInlineMarkdown(text)}
        </p>,
      );
    }

    paragraph = [];
  };

  const flushBullets = () => {
    if (bulletItems.length === 0) {
      return;
    }

    blocks.push(
      <ul key={`bullets-${blocks.length}`}>
        {bulletItems.map((item, index) => (
          <li key={`${item}-${index}`}>
            {renderInlineMarkdown(item)}
          </li>
        ))}
      </ul>,
    );

    bulletItems = [];
  };

  const flushNumbers = () => {
    if (numberedItems.length === 0) {
      return;
    }

    blocks.push(
      <ol key={`numbers-${blocks.length}`}>
        {numberedItems.map((item, index) => (
          <li key={`${item}-${index}`}>
            {renderInlineMarkdown(item)}
          </li>
        ))}
      </ol>,
    );

    numberedItems = [];
  };

  const flushAll = () => {
    flushParagraph();
    flushBullets();
    flushNumbers();
  };

  let insideCodeBlock = false;
  let codeLines: string[] = [];
  let codeLanguage = "";

  const flushCodeBlock = () => {
    if (!insideCodeBlock) {
      return;
    }

    blocks.push(
      <pre key={`code-${blocks.length}`}>
        <code>
          {codeLines.join("\n")}
        </code>
      </pre>,
    );

    codeLines = [];
    codeLanguage = "";
    insideCodeBlock = false;
  };

  lines.forEach((rawLine, index) => {
    const line = rawLine.trim();

    if (line.startsWith("```")) {
      if (!insideCodeBlock) {
        flushAll();

        insideCodeBlock = true;
        codeLanguage = line.slice(3).trim();

        void codeLanguage;

        return;
      }

      flushCodeBlock();
      return;
    }

    if (insideCodeBlock) {
      codeLines.push(rawLine);
      return;
    }

    if (!line) {
      flushAll();
      return;
    }

    const headingMatch = line.match(
      /^(#{1,3})\s+(.+)$/,
    );

    if (headingMatch) {
      flushAll();

      const level = headingMatch[1].length;
      const headingText = headingMatch[2];

      if (level === 1) {
        blocks.push(
          <h3 key={`heading-${index}`}>
            {renderInlineMarkdown(headingText)}
          </h3>,
        );
      } else if (level === 2) {
        blocks.push(
          <h4 key={`heading-${index}`}>
            {renderInlineMarkdown(headingText)}
          </h4>,
        );
      } else {
        blocks.push(
          <h5 key={`heading-${index}`}>
            {renderInlineMarkdown(headingText)}
          </h5>,
        );
      }

      return;
    }

    const bulletMatch = line.match(
      /^[-*•]\s+(.+)$/,
    );

    if (bulletMatch) {
      flushParagraph();
      flushNumbers();

      bulletItems.push(bulletMatch[1]);
      return;
    }

    const numberedMatch = line.match(
      /^\d+[.)]\s+(.+)$/,
    );

    if (numberedMatch) {
      flushParagraph();
      flushBullets();

      numberedItems.push(numberedMatch[1]);
      return;
    }

    flushBullets();
    flushNumbers();

    paragraph.push(line);
  });

  if (insideCodeBlock) {
    flushCodeBlock();
  }

  flushAll();

  if (blocks.length === 0) {
    return (
      <p>
        {renderInlineMarkdown(content)}
      </p>
    );
  }

  return <>{blocks}</>;
}

/* ==========================================================================
   Main Page
   ========================================================================== */

export default function ChatPage() {
  const [history, setHistory] = useState<
    ChatHistoryItem[]
  >([]);

  const [
    selectedConversationId,
    setSelectedConversationId,
  ] = useState<string | null>(null);

  const [messages, setMessages] = useState<
    ChatMessage[]
  >([WELCOME_MESSAGE]);

  const [input, setInput] = useState("");

  const [loadingHistory, setLoadingHistory] =
    useState(true);

  const [
    loadingConversation,
    setLoadingConversation,
  ] = useState(false);

  const [sending, setSending] = useState(false);

  const [
    deletingConversationId,
    setDeletingConversationId,
  ] = useState<string | null>(null);

  const [error, setError] =
    useState<string | null>(null);

  /*
   * Mobile / compact navigation menu.
   * The menu is intentionally local to ChatPage so it does not
   * interfere with the existing conversation state.
   */
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const menuRef =
    useRef<HTMLDivElement | null>(null);

  const navigate = useNavigate();
  const { logout } = useAuth();

  const messagesEndRef =
    useRef<HTMLDivElement | null>(null);

  const textareaRef =
    useRef<HTMLTextAreaElement | null>(null);

  const historyRequestId =
    useRef(0);

  const conversationRequestId =
    useRef(0);

  /* ------------------------------------------------------------------------
     Derived state
     ------------------------------------------------------------------------ */

  const selectedConversation = useMemo(
    () =>
      history.find(
        (item) =>
          String(item.id) ===
          selectedConversationId,
      ),
    [history, selectedConversationId],
  );

  const hasUserMessages = useMemo(
    () =>
      messages.some(
        (message) =>
          message.role === "user",
      ),
    [messages],
  );

  const canInteract =
    !sending &&
    !loadingConversation &&
    deletingConversationId === null;

  /* ------------------------------------------------------------------------
     Navigation menu
     ------------------------------------------------------------------------ */

  const closeMenu = useCallback(() => {
    setIsMenuOpen(false);
  }, []);

  const handleMenuNavigation = useCallback(
    (path: string) => {
      closeMenu();
      navigate(path);
    },
    [closeMenu, navigate],
  );

  const handleMenuLogout = useCallback(async () => {
    closeMenu();

    try {
      await logout();
    } finally {
      navigate("/login", { replace: true });
    }
  }, [closeMenu, logout, navigate]);

  useEffect(() => {
    if (!isMenuOpen) {
      return;
    }

    const handlePointerDown = (event: MouseEvent) => {
      const target = event.target;

      if (
        target instanceof Node &&
        !menuRef.current?.contains(target)
      ) {
        closeMenu();
      }
    };

    const handleKeyDown = (event: globalThis.KeyboardEvent) => {
      if (event.key === "Escape") {
        closeMenu();
      }
    };

    document.addEventListener(
      "mousedown",
      handlePointerDown,
    );
    document.addEventListener(
      "keydown",
      handleKeyDown,
    );

    return () => {
      document.removeEventListener(
        "mousedown",
        handlePointerDown,
      );
      document.removeEventListener(
        "keydown",
        handleKeyDown,
      );
    };
  }, [closeMenu, isMenuOpen]);

  /* ------------------------------------------------------------------------
     Focus input
     ------------------------------------------------------------------------ */

  const focusInput = useCallback(() => {
    window.setTimeout(() => {
      textareaRef.current?.focus();
    }, 40);
  }, []);

  /* ------------------------------------------------------------------------
     Auto resize textarea
     ------------------------------------------------------------------------ */

  const resizeTextarea = useCallback(() => {
    const textarea = textareaRef.current;

    if (!textarea) {
      return;
    }

    textarea.style.height = "auto";

    const nextHeight = Math.min(
      Math.max(textarea.scrollHeight, 24),
      160,
    );

    textarea.style.height = `${nextHeight}px`;
  }, []);

  useEffect(() => {
    resizeTextarea();
  }, [input, resizeTextarea]);

  /* ------------------------------------------------------------------------
     Load chat history
     ------------------------------------------------------------------------ */

  const loadHistory = useCallback(
    async (
      options?: {
        selectNewest?: boolean;
        preserveSelection?: boolean;
      },
    ) => {
      const requestId =
        ++historyRequestId.current;

      setLoadingHistory(true);

      try {
        const response =
          await getChatHistory();

        if (
          requestId !==
          historyRequestId.current
        ) {
          return [];
        }

        const normalized =
          normalizeHistory(response);

        setHistory(normalized);

        if (options?.selectNewest) {
          const newest = normalized[0];

          if (newest) {
            setSelectedConversationId(
              String(newest.id),
            );
          }
        } else if (
          options?.preserveSelection !== false
        ) {
          const currentStillExists =
            selectedConversationId &&
            normalized.some(
              (item) =>
                String(item.id) ===
                selectedConversationId,
            );

          if (
            !currentStillExists &&
            normalized.length > 0
          ) {
            setSelectedConversationId(
              String(normalized[0].id),
            );
          }
        }

        return normalized;
      } catch (err) {
        if (
          requestId !==
          historyRequestId.current
        ) {
          return [];
        }

        setError(
          getErrorMessage(err),
        );

        return [];
      } finally {
        if (
          requestId ===
          historyRequestId.current
        ) {
          setLoadingHistory(false);
        }
      }
    },
    [selectedConversationId],
  );

  useEffect(() => {
    void loadHistory({
      preserveSelection: false,
    });
  }, [loadHistory]);

  /* ------------------------------------------------------------------------
     Load selected conversation
     ------------------------------------------------------------------------ */

useEffect(() => {
  if (!selectedConversationId) {
    conversationRequestId.current += 1;

    setMessages([WELCOME_MESSAGE]);
    setLoadingConversation(false);

    return;
  }

  /*
   * Narrow the nullable state once.
   *
   * From this point onward TypeScript knows that
   * conversationId is always a string.
   */
  const conversationId = selectedConversationId;

  const requestId =
    ++conversationRequestId.current;

  let mounted = true;

  async function loadConversation(): Promise<void> {
    setLoadingConversation(true);
    setError(null);

    try {
      const conversation =
        await getChatConversation(conversationId);

      /*
       * Ignore stale responses when the user changes
       * conversations before the previous request finishes.
       */
      if (
        !mounted ||
        requestId !== conversationRequestId.current
      ) {
        return;
      }

      const loadedMessages =
        conversation.messages?.map((message) => ({
          id: String(message.id),

          role:
            message.role === "user"
              ? ("user" as const)
              : ("assistant" as const),

          content: message.content,

          time:
            formatTime(message.created_at) || "Now",
        })) ?? [];

      setMessages(
        loadedMessages.length > 0
          ? loadedMessages
          : [WELCOME_MESSAGE],
      );
    } catch (err) {
      if (
        !mounted ||
        requestId !== conversationRequestId.current
      ) {
        return;
      }

      setError(getErrorMessage(err));

      setMessages([WELCOME_MESSAGE]);
    } finally {
      if (
        mounted &&
        requestId === conversationRequestId.current
      ) {
        setLoadingConversation(false);
      }
    }
  }

  void loadConversation();

  return () => {
    mounted = false;
  };
}, [selectedConversationId]);
  /* ------------------------------------------------------------------------
     Scroll messages to bottom
     ------------------------------------------------------------------------ */

  useEffect(() => {
    const frame =
      window.requestAnimationFrame(() => {
        messagesEndRef.current?.scrollIntoView(
          {
            behavior: "smooth",
            block: "end",
          },
        );
      });

    return () =>
      window.cancelAnimationFrame(frame);
  }, [messages, sending]);

  /* ------------------------------------------------------------------------
     Focus after conversation changes
     ------------------------------------------------------------------------ */

  useEffect(() => {
    if (!loadingConversation) {
      focusInput();
    }
  }, [
    selectedConversationId,
    loadingConversation,
    focusInput,
  ]);

  /* ------------------------------------------------------------------------
     New conversation
     ------------------------------------------------------------------------ */

  const handleNewConversation = useCallback(() => {
    if (!canInteract) {
      return;
    }

    conversationRequestId.current += 1;

    setSelectedConversationId(null);
    setMessages([WELCOME_MESSAGE]);
    setInput("");
    setError(null);

    focusInput();
  }, [canInteract, focusInput]);

  /* ------------------------------------------------------------------------
     Select conversation
     ------------------------------------------------------------------------ */

  const handleSelectConversation = useCallback(
    (conversationId: string) => {
      if (
        !canInteract ||
        conversationId ===
          selectedConversationId
      ) {
        return;
      }

      setError(null);
      setSelectedConversationId(
        conversationId,
      );
    },
    [
      canInteract,
      selectedConversationId,
    ],
  );

  /* ------------------------------------------------------------------------
     Delete conversation
     ------------------------------------------------------------------------ */

  const handleDeleteConversation =
    useCallback(
      async (
        event: React.MouseEvent<HTMLButtonElement>,
        conversationId: string,
      ) => {
        event.stopPropagation();

        if (
          deletingConversationId ||
          sending ||
          loadingConversation
        ) {
          return;
        }

        const confirmed =
          window.confirm(
            "Delete this conversation?\n\nThis action cannot be undone.",
          );

        if (!confirmed) {
          return;
        }

        setDeletingConversationId(
          conversationId,
        );
        setError(null);

        try {
          await deleteChatConversation(
            conversationId,
          );

          const remaining =
            history.filter(
              (item) =>
                String(item.id) !==
                conversationId,
            );

          setHistory(remaining);

          if (
            selectedConversationId ===
            conversationId
          ) {
            if (remaining.length > 0) {
              setSelectedConversationId(
                String(
                  remaining[0].id,
                ),
              );
            } else {
              handleNewConversation();
            }
          }
        } catch (err) {
          setError(
            getErrorMessage(err),
          );
        } finally {
          setDeletingConversationId(
            null,
          );
        }
      },
      [
        deletingConversationId,
        sending,
        loadingConversation,
        history,
        selectedConversationId,
        handleNewConversation,
      ],
    );

  /* ------------------------------------------------------------------------
     Send chat message
     ------------------------------------------------------------------------ */

  const handleSubmit = useCallback(
    async (
      event?: FormEvent<HTMLFormElement>,
    ) => {
      event?.preventDefault();

      const message = input.trim();

      if (
        !message ||
        sending ||
        loadingConversation ||
        deletingConversationId
      ) {
        return;
      }

      setError(null);
      setInput("");

      const userMessage: ChatMessage = {
        id: createMessageId("user"),
        role: "user",
        content: message,
        time: getCurrentTime(),
      };

      setMessages((previous) => [
        ...previous,
        userMessage,
      ]);

      setSending(true);

      try {
        const response =
          (await sendChatMessage({
            message,
            collection_name:
              COLLECTION_NAME,
            top_k: TOP_K,
          })) as ChatResponseLike;

        const answer =
          response.answer ??
          response.response ??
          response.message ??
          "I couldn't generate a response.";

        const assistantMessage: ChatMessage = {
          id: createMessageId(
            "assistant",
          ),
          role: "assistant",
          content: answer,
          time: getCurrentTime(),
        };

        setMessages((previous) => [
          ...previous,
          assistantMessage,
        ]);

        /*
         * The backend returns conversation_id.
         * Use it directly instead of guessing which
         * conversation was created.
         */
        const returnedConversationId =
          getConversationId(response);

        if (returnedConversationId) {
          setSelectedConversationId(
            returnedConversationId,
          );
        }

        /*
         * Refresh the sidebar so the newly created
         * conversation and updated title appear immediately.
         */
        try {
          const refreshed =
            await getChatHistory();

          const normalized =
            normalizeHistory(
              refreshed,
            );

          setHistory(normalized);

          if (
            returnedConversationId
          ) {
            const exists =
              normalized.some(
                (item) =>
                  String(item.id) ===
                  returnedConversationId,
              );

            if (exists) {
              setSelectedConversationId(
                returnedConversationId,
              );
            }
          } else if (
            !selectedConversationId &&
            normalized.length > 0
          ) {
            setSelectedConversationId(
              String(
                normalized[0].id,
              ),
            );
          }
        } catch {
          /*
           * The actual chat succeeded.
           * A history refresh failure must
           * never remove the AI response.
           */
        }
      } catch (err) {
        const errorMessage =
          getErrorMessage(err);

        setError(errorMessage);

        setMessages((previous) => [
          ...previous,
          {
            id: createMessageId(
              "error",
            ),
            role: "assistant",
            content:
              `Sorry, I couldn't process that request.\n\n${errorMessage}`,
            time: getCurrentTime(),
          },
        ]);
      } finally {
        setSending(false);
        focusInput();
      }
    },
    [
      input,
      sending,
      loadingConversation,
      deletingConversationId,
      selectedConversationId,
      focusInput,
    ],
  );

  /* ------------------------------------------------------------------------
     Keyboard handling
     ------------------------------------------------------------------------ */

  const handleInputKeyDown = useCallback(
    (
      event: KeyboardEvent<HTMLTextAreaElement>,
    ) => {
      if (
        event.key === "Enter" &&
        !event.shiftKey
      ) {
        event.preventDefault();

        if (
          !sending &&
          !loadingConversation
        ) {
          void handleSubmit();
        }
      }
    },
    [
      sending,
      loadingConversation,
      handleSubmit,
    ],
  );

  /* ------------------------------------------------------------------------
     Suggestion
     ------------------------------------------------------------------------ */

  const handleSuggestion = useCallback(
    (text: string) => {
      if (!canInteract) {
        return;
      }

      setInput(text);
      focusInput();
    },
    [canInteract, focusInput],
  );

  /* ------------------------------------------------------------------------
     Render
     ------------------------------------------------------------------------ */

  return (
    <div className="chat-page">
      {/* Animated background */}
      <div
        className="chat-background-orb chat-background-orb-one"
        aria-hidden="true"
      />

      <div
        className="chat-background-orb chat-background-orb-two"
        aria-hidden="true"
      />

      <div
        className="chat-background-grid"
        aria-hidden="true"
      />

      <main className="chat-shell">
        {/* ==================================================================
            TOP BAR
        ================================================================== */}

        <header className="chat-topbar">
          <div className="chat-brand">
            <div className="chat-brand-icon">
              <Sparkles size={23} />
            </div>

            <div>
              <h1>Enterprise AI</h1>
              <span>
                Knowledge Workspace
              </span>
            </div>
          </div>

          <div className="chat-topbar-actions">
            <button
              type="button"
              className="new-chat-button"
              onClick={
                handleNewConversation
              }
              disabled={!canInteract}
              aria-label="Start a new chat"
            >
              <Plus size={18} />
              <span>New chat</span>
            </button>
          </div>
        </header>

        {/* ==================================================================
            MAIN LAYOUT
        ================================================================== */}

        <section className="chat-layout">
          {/* ================================================================
              HISTORY
          ================================================================ */}

          <aside
            className="chat-history"
            aria-label="Chat history"
          >
            <div className="history-header">
              <div>
                <h2>Chat history</h2>
                <p>
                  Your previous conversations
                </p>
              </div>

              <div
                ref={menuRef}
                className="history-menu"
              >
                <button
                  type="button"
                  className={`history-menu-button ${
                    isMenuOpen ? "is-open" : ""
                  }`}
                  onClick={() =>
                    setIsMenuOpen((open) => !open)
                  }
                  aria-label="Open workspace menu"
                  aria-expanded={isMenuOpen}
                  aria-haspopup="menu"
                  title="Workspace menu"
                >
                  {isMenuOpen ? (
                    <X size={20} aria-hidden="true" />
                  ) : (
                    <Menu size={20} aria-hidden="true" />
                  )}
                </button>

                {isMenuOpen && (
                  <div
                    className="history-menu-popover"
                    role="menu"
                    aria-label="Workspace navigation"
                  >
                    <div className="history-menu-heading">
                      <span>Workspace</span>
                      <small>Quick navigation</small>
                    </div>

                    <button
                      type="button"
                      className="history-menu-item"
                      role="menuitem"
                      onClick={() => {
                        closeMenu();
                        handleNewConversation();
                      }}
                      disabled={!canInteract}
                    >
                      <span className="history-menu-item-icon">
                        <Plus
                          size={17}
                          aria-hidden="true"
                        />
                      </span>

                      <span className="history-menu-item-copy">
                        <strong>New chat</strong>
                        <small>Start a fresh conversation</small>
                      </span>
                    </button>

                    <button
                      type="button"
                      className="history-menu-item"
                      role="menuitem"
                      onClick={() =>
                        handleMenuNavigation(
                          "/dashboard",
                        )
                      }
                    >
                      <span className="history-menu-item-icon">
                        <LayoutDashboard
                          size={17}
                          aria-hidden="true"
                        />
                      </span>

                      <span className="history-menu-item-copy">
                        <strong>Dashboard</strong>
                        <small>Workspace overview</small>
                      </span>
                    </button>

                    <button
                      type="button"
                      className="history-menu-item"
                      role="menuitem"
                      onClick={() =>
                        handleMenuNavigation(
                          "/documents",
                        )
                      }
                    >
                      <span className="history-menu-item-icon">
                        <FileText
                          size={17}
                          aria-hidden="true"
                        />
                      </span>

                      <span className="history-menu-item-copy">
                        <strong>Documents</strong>
                        <small>Manage your knowledge</small>
                      </span>
                    </button>

                    <button
                      type="button"
                      className="history-menu-item active"
                      role="menuitem"
                      onClick={() =>
                        handleMenuNavigation("/chat")
                      }
                    >
                      <span className="history-menu-item-icon">
                        <MessageSquare
                          size={17}
                          aria-hidden="true"
                        />
                      </span>

                      <span className="history-menu-item-copy">
                        <strong>AI Chat</strong>
                        <small>Ask your documents</small>
                      </span>
                    </button>

                    <button
                      type="button"
                      className="history-menu-item"
                      role="menuitem"
                      onClick={() =>
                        handleMenuNavigation(
                          "/profile",
                        )
                      }
                    >
                      <span className="history-menu-item-icon">
                        <User
                          size={17}
                          aria-hidden="true"
                        />
                      </span>

                      <span className="history-menu-item-copy">
                        <strong>Profile</strong>
                        <small>Account settings</small>
                      </span>
                    </button>

                    <div
                      className="history-menu-divider"
                      role="separator"
                    />

                    <button
                      type="button"
                      className="history-menu-item danger"
                      role="menuitem"
                      onClick={() =>
                        void handleMenuLogout()
                      }
                    >
                      <span className="history-menu-item-icon">
                        <LogOut
                          size={17}
                          aria-hidden="true"
                        />
                      </span>

                      <span className="history-menu-item-copy">
                        <strong>Sign out</strong>
                        <small>End this session</small>
                      </span>
                    </button>
                  </div>
                )}
              </div>
            </div>

            <button
              type="button"
              className="new-conversation-button"
              onClick={
                handleNewConversation
              }
              disabled={!canInteract}
            >
              <Plus size={19} />
              <span>
                New conversation
              </span>
            </button>

            <div
              className="history-list"
              aria-live="polite"
            >
              {loadingHistory ? (
                <div className="history-loading">
                  <span className="loading-dot" />
                  <span className="loading-dot" />
                  <span className="loading-dot" />

                  <p>
                    Loading conversations...
                  </p>
                </div>
              ) : history.length === 0 ? (
                <div className="history-empty">
                  <MessageSquare
                    size={26}
                    aria-hidden="true"
                  />

                  <p>
                    No conversations yet.
                  </p>

                  <span>
                    Start a new chat to
                    create one.
                  </span>
                </div>
              ) : (
                history.map(
                  (conversation) => {
                    const id =
                      String(
                        conversation.id,
                      );

                    const active =
                      id ===
                      selectedConversationId;

                    const deleting =
                      deletingConversationId ===
                      id;

                    return (
                      <div
                        key={id}
                        className={`history-item ${
                          active
                            ? "active"
                            : ""
                        }`}
                      >
                        <button
                          type="button"
                          className="history-item-main"
                          onClick={() =>
                            handleSelectConversation(
                              id,
                            )
                          }
                          disabled={
                            !canInteract
                          }
                          aria-current={
                            active
                              ? "page"
                              : undefined
                          }
                        >
                          <div className="history-item-icon">
                            <MessageSquare
                              size={17}
                              aria-hidden="true"
                            />
                          </div>

                          <div className="history-item-content">
                            <strong>
                              {
                                conversation.title
                              }
                            </strong>

                            <span>
                              {formatTime(
                                conversation.updated_at ??
                                  conversation.created_at,
                              )}
                            </span>
                          </div>
                        </button>

                        <button
                          type="button"
                          className="history-delete"
                          aria-label={`Delete ${
                            conversation.title
                          }`}
                          title="Delete conversation"
                          onClick={(
                            event,
                          ) =>
                            void handleDeleteConversation(
                              event,
                              id,
                            )
                          }
                          disabled={
                            deletingConversationId !==
                              null ||
                            sending ||
                            loadingConversation
                          }
                        >
                          {deleting ? (
                            <span
                              className="loading-spinner"
                              aria-hidden="true"
                            />
                          ) : (
                            <Trash2
                              size={15}
                              aria-hidden="true"
                            />
                          )}
                        </button>
                      </div>
                    );
                  },
                )
              )}
            </div>
          </aside>

          {/* ================================================================
              CHAT PANEL
          ================================================================ */}

          <section
            className="chat-panel"
            aria-label="AI chat"
          >
            {/* Assistant header */}
            <div className="assistant-header">
              <div className="assistant-identity">
                <div className="assistant-logo-wrapper">
                  <AiCatLogo />
                </div>

                <div>
                  <h2>
                    AI Assistant
                  </h2>

                  <p>
                    Ask questions about your
                    enterprise knowledge.
                  </p>
                </div>
              </div>

              <div
                className="ai-status"
                aria-label="AI status: online"
              >
                <span className="status-dot" />
                AI Online
              </div>
            </div>

            {/* Conversation title */}
            {selectedConversation && (
              <div
                className="conversation-title-bar"
                title={
                  selectedConversation.title
                }
              >
                <span>
                  {
                    selectedConversation.title
                  }
                </span>
              </div>
            )}

            {/* ==============================================================
                MESSAGES
            ============================================================== */}

            <div
              className="messages-area"
              aria-live="polite"
              aria-busy={
                loadingConversation ||
                sending
              }
            >
              {!hasUserMessages &&
                !loadingConversation && (
                  <div className="chat-welcome">
                    <div className="welcome-logo">
                      <AiCatLogo />
                    </div>

                    <h2>
                      How can I help you
                      today?
                    </h2>

                    <p>
                      Ask questions, summarize
                      documents, or explore
                      your knowledge base.
                    </p>
                  </div>
                )}

              {loadingConversation ? (
                <div
                  className="conversation-loading"
                  role="status"
                >
                  <div className="loading-spinner" />

                  <span>
                    Loading conversation...
                  </span>
                </div>
              ) : (
                <div className="message-list">
                  {messages.map(
                    (message) => (
                      <article
                        key={message.id}
                        className={`message-row ${
                          message.role
                        }`}
                      >
                        {message.role ===
                          "assistant" && (
                          <div className="message-avatar assistant-avatar">
                            <AiCatLogo />
                          </div>
                        )}

                        <div className="message-content">
                          <div className="message-author">
                            {message.role ===
                            "assistant"
                              ? "AI Assistant"
                              : "You"}
                          </div>

                          <div className="message-bubble">
                            {message.role ===
                            "assistant" ? (
                              <MarkdownMessage
                                content={
                                  message.content
                                }
                              />
                            ) : (
                              <p>
                                {
                                  message.content
                                }
                              </p>
                            )}
                          </div>

                          <time>
                            {message.time}
                          </time>
                        </div>

                        {message.role ===
                          "user" && (
                          <div className="message-avatar user-avatar">
                            <User
                              size={18}
                              aria-hidden="true"
                            />
                          </div>
                        )}
                      </article>
                    ),
                  )}

                  {/* AI typing indicator */}
                  {sending && (
                    <article className="message-row assistant">
                      <div className="message-avatar assistant-avatar">
                        <AiCatLogo />
                      </div>

                      <div className="message-content">
                        <div className="message-author">
                          AI Assistant
                        </div>

                        <div
                          className="message-bubble typing-bubble"
                          role="status"
                          aria-label="AI is thinking"
                        >
                          <span className="typing-dot" />
                          <span className="typing-dot" />
                          <span className="typing-dot" />
                        </div>

                        <time>
                          Thinking...
                        </time>
                      </div>
                    </article>
                  )}

                  <div
                    ref={
                      messagesEndRef
                    }
                    aria-hidden="true"
                  />
                </div>
              )}
            </div>

            {/* ==============================================================
                ERROR
            ============================================================== */}

            {error && (
              <div
                className="chat-error"
                role="alert"
              >
                <span>{error}</span>

                <button
                  type="button"
                  onClick={() =>
                    setError(null)
                  }
                  aria-label="Dismiss error"
                  title="Dismiss"
                >
                  <X size={16} />
                </button>
              </div>
            )}

            {/* ==============================================================
                SUGGESTIONS
            ============================================================== */}

            <div
              className="suggestions"
              aria-label="Suggested prompts"
            >
              {SUGGESTIONS.map(
                ({
                  icon: Icon,
                  title,
                  text,
                }) => (
                  <button
                    key={title}
                    type="button"
                    className="suggestion"
                    onClick={() =>
                      handleSuggestion(
                        text,
                      )
                    }
                    disabled={!canInteract}
                    title={text}
                  >
                    <Icon
                      size={17}
                      aria-hidden="true"
                    />

                    <span>{title}</span>
                  </button>
                ),
              )}
            </div>

            {/* ==============================================================
                COMPOSER
            ============================================================== */}

            <form
              className="chat-composer"
              onSubmit={handleSubmit}
            >
              <div className="composer-input-wrapper">
                <MessageSquare
                  size={20}
                  className="composer-icon"
                  aria-hidden="true"
                />

                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={(event) =>
                    setInput(
                      event.target.value,
                    )
                  }
                  onKeyDown={
                    handleInputKeyDown
                  }
                  placeholder="Ask anything about your documents..."
                  rows={1}
                  maxLength={
                    MAX_MESSAGE_LENGTH
                  }
                  disabled={
                    sending ||
                    loadingConversation
                  }
                  aria-label="Chat message"
                  aria-describedby="chat-composer-hint"
                />

                <button
                  type="submit"
                  className="send-button"
                  disabled={
                    !input.trim() ||
                    sending ||
                    loadingConversation
                  }
                  aria-label="Send message"
                  title="Send message"
                >
                  <Send
                    size={19}
                    aria-hidden="true"
                  />
                </button>
              </div>

              <div
                className="composer-footer"
                id="chat-composer-hint"
              >
                <span>
                  <Sparkles
                    size={13}
                    aria-hidden="true"
                  />

                  AI responses are generated
                  from your workspace knowledge.
                </span>

                <span className="character-count">
                  {input.length > 0
                    ? `${input.length}/${MAX_MESSAGE_LENGTH}`
                    : ""}
                </span>
              </div>
            </form>
          </section>
        </section>
      </main>
    </div>
  );
}