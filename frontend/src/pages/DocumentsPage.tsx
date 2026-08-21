import {
  AlertCircle,
  CheckCircle2,
  CloudUpload,
  FileText,
  Loader2,
  RefreshCw,
  Trash2,
  Upload,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ChangeEvent,
} from "react";
import { Link } from "react-router-dom";

import {
  deleteDocument,
  getDocuments,
  uploadDocument,
  type Document,
} from "../services/api";

import "./DocumentsPage.css";

const ACCEPTED_EXTENSIONS = [
  ".pdf",
  ".docx",
  ".txt",
  ".csv",
  ".xlsx",
] as const;

const ACCEPTED_MIME_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "text/plain",
  "text/csv",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
] as const;

const MAX_FILE_SIZE = 20 * 1024 * 1024;

function getDocumentName(document: Document): string {
  return (
    document.original_filename ||
    document.filename ||
    document.file_name ||
    "Unnamed document"
  );
}

function formatFileSize(size?: number): string {
  if (!size || size <= 0) {
    return "Unknown size";
  }

  if (size < 1024) {
    return `${size} B`;
  }

  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  }

  if (size < 1024 * 1024 * 1024) {
    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  }

  return `${(size / (1024 * 1024 * 1024)).toFixed(1)} GB`;
}

function getFileExtension(filename: string): string {
  const dotIndex = filename.lastIndexOf(".");

  if (dotIndex === -1) {
    return "";
  }

  return filename.slice(dotIndex).toLowerCase();
}

function getFileTypeLabel(document: Document): string {
  const filename = getDocumentName(document);
  const extension = getFileExtension(filename);

  if (extension) {
    return extension.replace(".", "").toUpperCase();
  }

  if (document.content_type) {
    const subtype = document.content_type.split("/").pop();

    if (subtype) {
      return subtype.toUpperCase();
    }
  }

  return "FILE";
}

function getStatusLabel(status?: string): string {
  if (!status) {
    return "Available";
  }

  return status
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (character) => character.toUpperCase());
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
            detail?: string | Array<unknown>;
          };
        };
      }
    ).response;

    const detail = response?.data?.detail;

    if (typeof detail === "string" && detail.trim()) {
      return detail;
    }

    if (Array.isArray(detail)) {
      return "The server rejected the request. Please check your input.";
    }
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  return "Something went wrong. Please try again.";
}

function isSupportedFile(file: File): boolean {
  const filename = file.name.toLowerCase();

  const extensionAllowed = ACCEPTED_EXTENSIONS.some((extension) =>
    filename.endsWith(extension),
  );

  const mimeAllowed =
    !file.type ||
    ACCEPTED_MIME_TYPES.includes(
      file.type as (typeof ACCEPTED_MIME_TYPES)[number],
    );

  return extensionAllowed && mimeAllowed;
}

function getDocumentStatusClass(status?: string): string {
  const normalized = status?.toLowerCase().trim();

  if (
    normalized === "failed" ||
    normalized === "error"
  ) {
    return "document-status-error";
  }

  if (
    normalized === "processing" ||
    normalized === "pending"
  ) {
    return "document-status-processing";
  }

  return "document-status-ready";
}

export default function DocumentsPage() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const mountedRef = useRef(true);

  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [deletingId, setDeletingId] = useState<
    string | number | null
  >(null);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadDocuments = useCallback(async () => {
    if (mountedRef.current) {
      setError("");
    }

    try {
      const result = await getDocuments();

      if (!mountedRef.current) {
        return;
      }

      setDocuments(Array.isArray(result) ? result : []);
    } catch (requestError) {
      if (!mountedRef.current) {
        return;
      }

      setError(getErrorMessage(requestError));
    } finally {
      if (mountedRef.current) {
        setIsLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    mountedRef.current = true;

    void loadDocuments();

    return () => {
      mountedRef.current = false;
    };
  }, [loadDocuments]);

  const openFilePicker = () => {
    if (isUploading) {
      return;
    }

    fileInputRef.current?.click();
  };

  const validateFile = (file: File): string | null => {
    if (!file.name.trim()) {
      return "Please select a valid file.";
    }

    if (!isSupportedFile(file)) {
      return "Unsupported file type. Please upload PDF, DOCX, TXT, CSV, or XLSX.";
    }

    if (file.size <= 0) {
      return "The selected file is empty.";
    }

    if (file.size > MAX_FILE_SIZE) {
      return "File is too large. Maximum allowed size is 20 MB.";
    }

    return null;
  };

  const handleUpload = async (file: File) => {
    setError("");
    setSuccess("");

    const validationError = validateFile(file);

    if (validationError) {
      setError(validationError);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      return;
    }

    setIsUploading(true);

    try {
      const uploadedDocument = await uploadDocument(file);

      if (!mountedRef.current) {
        return;
      }

      setDocuments((current) => [
        uploadedDocument,
        ...current.filter(
          (document) => document.id !== uploadedDocument.id,
        ),
      ]);

      setSuccess(
        `"${file.name}" uploaded successfully.`,
      );
    } catch (requestError) {
      if (!mountedRef.current) {
        return;
      }

      setError(getErrorMessage(requestError));
    } finally {
      if (mountedRef.current) {
        setIsUploading(false);
      }

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleFileChange = (
    event: ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    void handleUpload(file);
  };

  const handleDelete = async (
    document: Document,
  ) => {
    const documentId = document.id;
    const documentName = getDocumentName(document);

    const confirmed = window.confirm(
      `Delete "${documentName}"?\n\nThis action cannot be undone.`,
    );

    if (!confirmed) {
      return;
    }

    setError("");
    setSuccess("");
    setDeletingId(documentId);

    try {
      await deleteDocument(documentId);

      if (!mountedRef.current) {
        return;
      }

      setDocuments((current) =>
        current.filter(
          (item) => item.id !== documentId,
        ),
      );

      setSuccess(
        `"${documentName}" was deleted successfully.`,
      );
    } catch (requestError) {
      if (!mountedRef.current) {
        return;
      }

      setError(getErrorMessage(requestError));
    } finally {
      if (mountedRef.current) {
        setDeletingId(null);
      }
    }
  };

  const documentCount = documents.length;

  return (
    <main className="documents-page">
      <div
        className="documents-background"
        aria-hidden="true"
      >
        <div className="documents-grid" />

        <div className="documents-orb documents-orb-one" />
        <div className="documents-orb documents-orb-two" />
      </div>

      <div className="documents-container">
        <header className="documents-header glass-document-card">
          <Link
            to="/dashboard"
            className="documents-brand"
            aria-label="Back to Enterprise AI dashboard"
          >
            <div className="documents-brand-icon">
              <FileText size={21} />
            </div>

            <div>
              <strong>Enterprise AI</strong>
              <span>Document workspace</span>
            </div>
          </Link>

          <Link
            to="/dashboard"
            className="documents-back-link"
          >
            ← Dashboard
          </Link>
        </header>

        <section className="documents-intro">
          <div>
            <span className="documents-eyebrow">
              KNOWLEDGE BASE
            </span>

            <h1>
              Your documents,
              <span> intelligently managed.</span>
            </h1>

            <p>
              Upload your files and turn them into searchable,
              AI-ready knowledge.
            </p>
          </div>
        </section>

        {error && (
          <div
            className="documents-message documents-error"
            role="alert"
          >
            <AlertCircle size={18} />

            <span>{error}</span>

            <button
              type="button"
              onClick={() => setError("")}
              aria-label="Dismiss error"
            >
              ×
            </button>
          </div>
        )}

        {success && (
          <div
            className="documents-message documents-success"
            role="status"
          >
            <CheckCircle2 size={18} />

            <span>{success}</span>

            <button
              type="button"
              onClick={() => setSuccess("")}
              aria-label="Dismiss success message"
            >
              ×
            </button>
          </div>
        )}

        <section className="upload-section">
          <input
            ref={fileInputRef}
            type="file"
            hidden
            accept=".pdf,.docx,.txt,.csv,.xlsx"
            onChange={handleFileChange}
            disabled={isUploading}
          />

          <button
            type="button"
            className="document-upload-card"
            onClick={openFilePicker}
            disabled={isUploading}
            aria-label="Upload a document"
          >
            <div className="upload-icon">
              {isUploading ? (
                <Loader2
                  size={30}
                  className="documents-spinner"
                />
              ) : (
                <CloudUpload size={30} />
              )}
            </div>

            <div className="upload-content">
              <h2>
                {isUploading
                  ? "Uploading document..."
                  : "Upload a document"}
              </h2>

              <p>
                {isUploading
                  ? "Please wait while your document is being processed."
                  : "Click here to select a file from your computer."}
              </p>

              <span>
                PDF · DOCX · TXT · CSV · XLSX · Max 20 MB
              </span>
            </div>

            {!isUploading && (
              <div className="upload-button">
                <Upload size={16} />
                Choose file
              </div>
            )}
          </button>
        </section>

        <section className="documents-list-section">
          <div className="documents-section-heading">
            <div>
              <span className="documents-eyebrow">
                LIBRARY
              </span>

              <h2>Your documents</h2>
            </div>

            <div className="documents-heading-actions">
              <span className="documents-count">
                {documentCount}{" "}
                {documentCount === 1
                  ? "document"
                  : "documents"}
              </span>

              {!isLoading && (
                <button
                  type="button"
                  className="documents-refresh-button"
                  onClick={() => void loadDocuments()}
                  aria-label="Refresh documents"
                  title="Refresh documents"
                >
                  <RefreshCw size={16} />
                </button>
              )}
            </div>
          </div>

          {isLoading ? (
            <div
              className="documents-loading glass-document-card"
              role="status"
            >
              <Loader2
                size={25}
                className="documents-spinner"
              />

              <span>
                Loading your documents...
              </span>
            </div>
          ) : documents.length === 0 ? (
            <div className="documents-empty glass-document-card">
              <div className="empty-icon">
                <FileText size={27} />
              </div>

              <h3>No documents yet</h3>

              <p>
                Upload your first document to start building
                your AI knowledge base.
              </p>

              <button
                type="button"
                onClick={openFilePicker}
                disabled={isUploading}
              >
                <Upload size={16} />
                Upload first document
              </button>
            </div>
          ) : (
            <div className="documents-list">
              {documents.map((document) => {
                const documentId = document.id;
                const isDeleting =
                  deletingId === documentId;

                const documentName =
                  getDocumentName(document);

                const fileType =
                  getFileTypeLabel(document);

                const status =
                  getStatusLabel(document.status);

                const statusClass =
                  getDocumentStatusClass(
                    document.status,
                  );

                return (
                  <article
                    key={String(documentId)}
                    className="document-item glass-document-card"
                  >
                    <div
                      className="document-file-icon"
                      aria-hidden="true"
                    >
                      <FileText size={22} />
                    </div>

                    <div className="document-info">
                      <h3 title={documentName}>
                        {documentName}
                      </h3>

                      <div className="document-meta">
                        <span>
                          {formatFileSize(document.size)}
                        </span>

                        <span>•</span>

                        <span>{fileType}</span>

                        <span>•</span>

                        <span
                          className={`document-status ${statusClass}`}
                        >
                          {status}
                        </span>
                      </div>
                    </div>

                    <button
                      type="button"
                      className="document-delete-button"
                      onClick={() =>
                        void handleDelete(document)
                      }
                      disabled={isDeleting}
                      aria-label={`Delete ${documentName}`}
                      title={`Delete ${documentName}`}
                    >
                      {isDeleting ? (
                        <Loader2
                          size={18}
                          className="documents-spinner"
                        />
                      ) : (
                        <Trash2 size={18} />
                      )}
                    </button>
                  </article>
                );
              })}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}