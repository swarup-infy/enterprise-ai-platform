import {
  ArrowRight,
  CheckCircle2,
  Eye,
  EyeOff,
  FileText,
  Loader2,
  Lock,
  Mail,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import {
  useEffect,
  useId,
  useState,
  type FormEvent,
} from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import "./LoginPage.css";

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
      return "The server rejected your credentials. Please check your email and password.";
    }
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  return "Unable to sign in. Please try again.";
}

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const emailId = useId();
  const passwordId = useId();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    document.title = "Sign in | Enterprise AI";

    return () => {
      document.title = "Enterprise AI Platform";
    };
  }, []);

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    if (isSubmitting) {
      return;
    }

    setError("");

    const normalizedEmail = email.trim();

    if (!normalizedEmail) {
      setError("Please enter your email address.");
      return;
    }

    if (!normalizedEmail.includes("@")) {
      setError("Please enter a valid email address.");
      return;
    }

    if (!password) {
      setError("Please enter your password.");
      return;
    }

    setIsSubmitting(true);

    try {
      await login({
        email: normalizedEmail,
        password,
      });

      navigate("/dashboard", {
        replace: true,
      });
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="auth-page">
      <div
        className="auth-background"
        aria-hidden="true"
      >
        <div className="auth-grid" />

        <div className="auth-orb auth-orb-one" />
        <div className="auth-orb auth-orb-two" />
        <div className="auth-orb auth-orb-three" />
      </div>

      <div className="auth-shell">
        {/* ==================================================================
            Brand / Product side
            ================================================================== */}

        <section
          className="auth-brand-panel"
          aria-label="Enterprise AI introduction"
        >
          <Link
            to="/"
            className="auth-brand"
            aria-label="Enterprise AI home"
          >
            <span className="auth-brand-icon">
              <FileText
                size={22}
                strokeWidth={2.2}
              />
            </span>

            <span className="auth-brand-name">
              Enterprise AI
            </span>

            <span className="auth-brand-dot" />
          </Link>

          <div className="auth-brand-content">
            <div className="auth-eyebrow">
              <Sparkles size={13} />
              AI-POWERED KNOWLEDGE
            </div>

            <h1>
              Your documents.
              <span> Supercharged by AI.</span>
            </h1>

            <p>
              Upload, search, understand, and chat with your
              documents inside one intelligent workspace.
            </p>

            <div className="auth-feature-list">
              <div className="auth-feature">
                <span className="auth-feature-icon">
                  <CheckCircle2 size={15} />
                </span>

                <span>
                  Intelligent document search
                </span>
              </div>

              <div className="auth-feature">
                <span className="auth-feature-icon">
                  <CheckCircle2 size={15} />
                </span>

                <span>
                  AI-powered document conversations
                </span>
              </div>

              <div className="auth-feature">
                <span className="auth-feature-icon">
                  <CheckCircle2 size={15} />
                </span>

                <span>
                  Secure personal workspace
                </span>
              </div>
            </div>
          </div>

          <div className="auth-trust">
            <span className="auth-trust-icon">
              <ShieldCheck size={17} />
            </span>

            <div>
              <strong>Private by design</strong>
              <span>
                Your workspace is protected by
                authenticated access.
              </span>
            </div>
          </div>
        </section>

        {/* ==================================================================
            Login form
            ================================================================== */}

        <section
          className="auth-form-panel"
          aria-label="Sign in"
        >
          <div className="auth-form-container">
            <div className="auth-mobile-brand">
              <Link
                to="/"
                className="auth-mobile-brand-link"
                aria-label="Enterprise AI home"
              >
                <span className="auth-brand-icon">
                  <FileText
                    size={21}
                    strokeWidth={2.2}
                  />
                </span>

                <span>Enterprise AI</span>
              </Link>
            </div>

            <div className="auth-heading">
              <span className="auth-heading-label">
                WELCOME BACK
              </span>

              <h2>Sign in to your workspace</h2>

              <p>
                Continue where you left off with your
                documents and AI conversations.
              </p>
            </div>

            <form
              className="auth-form"
              onSubmit={handleSubmit}
              noValidate
            >
              {error && (
                <div
                  className="auth-error"
                  role="alert"
                  aria-live="polite"
                >
                  <span className="auth-error-mark">
                    !
                  </span>

                  <span>{error}</span>
                </div>
              )}

              {/* Email */}

              <div className="form-field">
                <label htmlFor={emailId}>
                  Email address
                </label>

                <div
                  className={`input-wrapper ${
                    email
                      ? "input-wrapper-filled"
                      : ""
                  }`}
                >
                  <Mail
                    className="input-icon"
                    size={18}
                    aria-hidden="true"
                  />

                  <input
                    id={emailId}
                    name="email"
                    type="email"
                    inputMode="email"
                    autoComplete="email"
                    autoCapitalize="none"
                    spellCheck={false}
                    placeholder="you@example.com"
                    value={email}
                    onChange={(event) => {
                      setEmail(event.target.value);

                      if (error) {
                        setError("");
                      }
                    }}
                    disabled={isSubmitting}
                    aria-invalid={Boolean(error)}
                    required
                  />
                </div>
              </div>

              {/* Password */}

              <div className="form-field">
                <div className="field-label-row">
                  <label htmlFor={passwordId}>
                    Password
                  </label>
                </div>

                <div
                  className={`input-wrapper ${
                    password
                      ? "input-wrapper-filled"
                      : ""
                  }`}
                >
                  <Lock
                    className="input-icon"
                    size={18}
                    aria-hidden="true"
                  />

                  <input
                    id={passwordId}
                    name="password"
                    type={
                      showPassword
                        ? "text"
                        : "password"
                    }
                    autoComplete="current-password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(event) => {
                      setPassword(event.target.value);

                      if (error) {
                        setError("");
                      }
                    }}
                    disabled={isSubmitting}
                    aria-invalid={Boolean(error)}
                    required
                  />

                  <button
                    type="button"
                    className="password-toggle"
                    aria-label={
                      showPassword
                        ? "Hide password"
                        : "Show password"
                    }
                    aria-pressed={showPassword}
                    onClick={() =>
                      setShowPassword(
                        (visible) => !visible,
                      )
                    }
                    disabled={isSubmitting}
                  >
                    {showPassword ? (
                      <EyeOff size={18} />
                    ) : (
                      <Eye size={18} />
                    )}
                  </button>
                </div>
              </div>

              {/* Submit */}

              <button
                type="submit"
                className="auth-submit-button"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <Loader2
                      size={18}
                      className="auth-spinner"
                      aria-hidden="true"
                    />

                    <span>Signing you in...</span>
                  </>
                ) : (
                  <>
                    <span>Sign in</span>

                    <ArrowRight
                      size={17}
                      aria-hidden="true"
                    />
                  </>
                )}
              </button>
            </form>

            <div className="auth-divider">
              <span />
              <span>OR</span>
              <span />
            </div>

            <p className="auth-switch">
              New to Enterprise AI?{" "}
              <Link to="/register">
                Create an account
                <ArrowRight size={14} />
              </Link>
            </p>

            <Link
              to="/"
              className="auth-back-link"
            >
              ← Back to home
            </Link>

            <div className="auth-footer">
              <Lock size={12} />
              <span>
                Securely authenticated workspace
              </span>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}