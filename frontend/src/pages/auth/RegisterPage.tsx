import {
  Check,
  CheckCircle2,
  Eye,
  EyeOff,
  FileText,
  Loader2,
  Lock,
  Mail,
  ShieldCheck,
  User,
  UserRoundPlus,
} from "lucide-react";
import {
  useMemo,
  useState,
  type FormEvent,
} from "react";
import {
  Link,
  useLocation,
  useNavigate,
} from "react-router-dom";

import { useAuth } from "../../context/AuthContext";

import "./LoginPage.css";

interface RegistrationLocationState {
  email?: string;
  registered?: boolean;
}

interface PasswordStrength {
  score: number;
  label: string;
  className: string;
}

interface PasswordRequirement {
  label: string;
  valid: boolean;
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
            detail?: string | Array<{ msg?: string }>;
          };
        };
      }
    ).response;

    const detail = response?.data?.detail;

    if (typeof detail === "string" && detail.trim()) {
      return detail.trim();
    }

    if (Array.isArray(detail)) {
      const messages = detail
        .map((item) => item?.msg?.trim())
        .filter(
          (message): message is string =>
            Boolean(message),
        );

      if (messages.length > 0) {
        return messages.join(", ");
      }
    }
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  return "Unable to create your account. Please try again.";
}

function getPasswordStrength(
  password: string,
): PasswordStrength {
  let score = 0;

  if (password.length >= 8) score += 1;
  if (/[A-Z]/.test(password)) score += 1;
  if (/[a-z]/.test(password)) score += 1;
  if (/\d/.test(password)) score += 1;
  if (/[^A-Za-z0-9]/.test(password)) score += 1;

  if (!password) {
    return {
      score: 0,
      label: "",
      className: "",
    };
  }

  if (score <= 2) {
    return {
      score,
      label: "Weak",
      className: "password-strength-weak",
    };
  }

  if (score <= 4) {
    return {
      score,
      label: "Good",
      className: "password-strength-good",
    };
  }

  return {
    score,
    label: "Strong",
    className: "password-strength-strong",
  };
}

function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isValidUsername(username: string): boolean {
  return /^[a-zA-Z0-9_.-]{3,30}$/.test(username);
}

export default function RegisterPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const { register } = useAuth();

  const [fullName, setFullName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] =
    useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  const passwordStrength = useMemo(
    () => getPasswordStrength(password),
    [password],
  );

  const passwordRequirements = useMemo<
    PasswordRequirement[]
  >(
    () => [
      {
        label: "At least 8 characters",
        valid: password.length >= 8,
      },
      {
        label: "One uppercase letter",
        valid: /[A-Z]/.test(password),
      },
      {
        label: "One number",
        valid: /\d/.test(password),
      },
    ],
    [password],
  );

  const passwordsMatch =
    confirmPassword.length > 0 &&
    password === confirmPassword;

  const registeredEmail =
    (
      location.state as
        | RegistrationLocationState
        | null
        | undefined
    )?.email ?? "";

  const clearError = () => {
    if (error) {
      setError("");
    }
  };

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    if (isSubmitting) {
      return;
    }

    setError("");

    const normalizedFullName = fullName.trim();
    const normalizedUsername = username.trim();
    const normalizedEmail = email.trim().toLowerCase();

    if (!normalizedFullName) {
      setError("Please enter your full name.");
      return;
    }

    if (normalizedFullName.length < 2) {
      setError(
        "Full name must contain at least 2 characters.",
      );
      return;
    }

    if (!normalizedUsername) {
      setError("Please enter your username.");
      return;
    }

    if (!isValidUsername(normalizedUsername)) {
      setError(
        "Username must be 3-30 characters and contain only letters, numbers, dots, underscores, or hyphens.",
      );
      return;
    }

    if (!normalizedEmail) {
      setError("Please enter your email address.");
      return;
    }

    if (!isValidEmail(normalizedEmail)) {
      setError("Please enter a valid email address.");
      return;
    }

    if (!password) {
      setError("Please create a password.");
      return;
    }

    if (password.length < 8) {
      setError(
        "Password must be at least 8 characters.",
      );
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setIsSubmitting(true);

    try {
      await register({
        full_name: normalizedFullName,
        username: normalizedUsername,
        email: normalizedEmail,
        password,
      });

      navigate("/login", {
        replace: true,
        state: {
          registered: true,
          email: normalizedEmail,
        },
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
        <div className="auth-orb auth-orb-one" />
        <div className="auth-orb auth-orb-two" />
        <div className="auth-orb auth-orb-three" />
        <div className="auth-grid" />
      </div>

      <section
        className="auth-shell auth-register-shell"
        aria-labelledby="register-heading"
      >
        {/* Brand panel */}

        <div className="auth-brand-panel">
          <Link
            to="/"
            className="auth-brand"
            aria-label="Enterprise AI home"
          >
            <div className="auth-brand-icon">
              <FileText
                size={24}
                strokeWidth={2.2}
                aria-hidden="true"
              />
            </div>

            <span>Enterprise AI</span>
          </Link>

          <div className="auth-brand-content">
            <span className="auth-eyebrow">
              AI-powered workspace
            </span>

            <h1>
              Build your
              <span> intelligent workspace.</span>
            </h1>

            <p>
              Create your account and transform your
              documents into searchable, AI-powered
              knowledge.
            </p>
          </div>

          <div className="auth-feature-list">
            <div className="auth-feature">
              <div className="auth-feature-icon">
                <CheckCircle2
                  size={17}
                  aria-hidden="true"
                />
              </div>

              <div>
                <strong>
                  Secure document workspace
                </strong>

                <span>
                  Keep your knowledge organized in one
                  place.
                </span>
              </div>
            </div>

            <div className="auth-feature">
              <div className="auth-feature-icon">
                <CheckCircle2
                  size={17}
                  aria-hidden="true"
                />
              </div>

              <div>
                <strong>
                  AI-powered conversations
                </strong>

                <span>
                  Ask questions and get answers from your
                  data.
                </span>
              </div>
            </div>

            <div className="auth-feature">
              <div className="auth-feature-icon">
                <CheckCircle2
                  size={17}
                  aria-hidden="true"
                />
              </div>

              <div>
                <strong>
                  Semantic document search
                </strong>

                <span>
                  Find relevant information faster with AI.
                </span>
              </div>
            </div>
          </div>

          <div className="auth-trust">
            <ShieldCheck
              size={18}
              aria-hidden="true"
            />

            <span>
              Secure authentication and protected workspace
            </span>
          </div>
        </div>

        {/* Form panel */}

        <div className="auth-form-panel">
          <div className="auth-form-container">
            <Link
              to="/"
              className="auth-mobile-brand auth-mobile-brand-link"
              aria-label="Enterprise AI home"
            >
              <div className="auth-brand-icon">
                <FileText
                  size={22}
                  strokeWidth={2.2}
                  aria-hidden="true"
                />
              </div>

              <span>Enterprise AI</span>
            </Link>

            <div className="auth-heading">
              <div className="auth-heading-icon">
                <UserRoundPlus
                  size={20}
                  aria-hidden="true"
                />
              </div>

              <div>
                <h2 id="register-heading">
                  Create your account
                </h2>

                <p>
                  Get started with your AI document
                  workspace.
                </p>
              </div>
            </div>

            {registeredEmail && (
              <div
                className="auth-success"
                role="status"
                aria-live="polite"
              >
                Account created successfully. You can now
                sign in with{" "}
                <strong>{registeredEmail}</strong>.
              </div>
            )}

            <form
              className="auth-form"
              onSubmit={handleSubmit}
              noValidate
            >
              {error && (
                <div
                  className="auth-error"
                  role="alert"
                  aria-live="assertive"
                >
                  {error}
                </div>
              )}

              {/* Full name */}

              <div className="form-field">
                <label htmlFor="fullName">
                  Full name
                </label>

                <div className="input-wrapper">
                  <User
                    className="input-icon"
                    size={18}
                    aria-hidden="true"
                  />

                  <input
                    id="fullName"
                    name="full_name"
                    type="text"
                    autoComplete="name"
                    placeholder="Enter your full name"
                    value={fullName}
                    onChange={(event) => {
                      setFullName(event.target.value);
                      clearError();
                    }}
                    disabled={isSubmitting}
                    maxLength={100}
                    required
                  />
                </div>
              </div>

              {/* Username */}

              <div className="form-field">
                <label htmlFor="username">
                  Username
                </label>

                <div className="input-wrapper">
                  <User
                    className="input-icon"
                    size={18}
                    aria-hidden="true"
                  />

                  <input
                    id="username"
                    name="username"
                    type="text"
                    autoComplete="username"
                    placeholder="Choose a username"
                    value={username}
                    onChange={(event) => {
                      setUsername(event.target.value);
                      clearError();
                    }}
                    disabled={isSubmitting}
                    maxLength={30}
                    required
                  />
                </div>

                <span className="field-hint">
                  3-30 characters
                </span>
              </div>

              {/* Email */}

              <div className="form-field">
                <label htmlFor="email">
                  Email address
                </label>

                <div className="input-wrapper">
                  <Mail
                    className="input-icon"
                    size={18}
                    aria-hidden="true"
                  />

                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(event) => {
                      setEmail(event.target.value);
                      clearError();
                    }}
                    disabled={isSubmitting}
                    maxLength={254}
                    required
                  />
                </div>
              </div>

              {/* Password */}

              <div className="form-field">
                <div className="field-label-row">
                  <label htmlFor="password">
                    Password
                  </label>

                  {passwordStrength.label && (
                    <span
                      className={`password-strength-label ${passwordStrength.className}`}
                    >
                      {passwordStrength.label}
                    </span>
                  )}
                </div>

                <div className="input-wrapper">
                  <Lock
                    className="input-icon"
                    size={18}
                    aria-hidden="true"
                  />

                  <input
                    id="password"
                    name="password"
                    type={
                      showPassword
                        ? "text"
                        : "password"
                    }
                    autoComplete="new-password"
                    placeholder="Create a password"
                    value={password}
                    onChange={(event) => {
                      setPassword(event.target.value);
                      clearError();
                    }}
                    disabled={isSubmitting}
                    maxLength={128}
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
                    onClick={() =>
                      setShowPassword(
                        (visible) => !visible,
                      )
                    }
                    disabled={isSubmitting}
                  >
                    {showPassword ? (
                      <EyeOff
                        size={18}
                        aria-hidden="true"
                      />
                    ) : (
                      <Eye
                        size={18}
                        aria-hidden="true"
                      />
                    )}
                  </button>
                </div>

                {password.length > 0 && (
                  <div
                    className="password-strength"
                    aria-live="polite"
                  >
                    <div
                      className="password-strength-bars"
                      aria-hidden="true"
                    >
                      {Array.from(
                        { length: 5 },
                        (_, index) => (
                          <span
                            key={index}
                            className={
                              index <
                              passwordStrength.score
                                ? passwordStrength.className
                                : ""
                            }
                          />
                        ),
                      )}
                    </div>

                    <div className="password-requirements">
                      {passwordRequirements.map(
                        (requirement) => (
                          <span
                            key={requirement.label}
                            className={
                              requirement.valid
                                ? "valid"
                                : ""
                            }
                          >
                            <Check
                              size={12}
                              aria-hidden="true"
                            />

                            {requirement.label}
                          </span>
                        ),
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Confirm password */}

              <div className="form-field">
                <div className="field-label-row">
                  <label htmlFor="confirmPassword">
                    Confirm password
                  </label>

                  {passwordsMatch && (
                    <span className="password-match">
                      <Check
                        size={13}
                        aria-hidden="true"
                      />
                      Matches
                    </span>
                  )}
                </div>

                <div className="input-wrapper">
                  <Lock
                    className="input-icon"
                    size={18}
                    aria-hidden="true"
                  />

                  <input
                    id="confirmPassword"
                    name="confirm_password"
                    type={
                      showConfirmPassword
                        ? "text"
                        : "password"
                    }
                    autoComplete="new-password"
                    placeholder="Confirm your password"
                    value={confirmPassword}
                    onChange={(event) => {
                      setConfirmPassword(
                        event.target.value,
                      );
                      clearError();
                    }}
                    disabled={isSubmitting}
                    maxLength={128}
                    required
                  />

                  <button
                    type="button"
                    className="password-toggle"
                    aria-label={
                      showConfirmPassword
                        ? "Hide password"
                        : "Show password"
                    }
                    onClick={() =>
                      setShowConfirmPassword(
                        (visible) => !visible,
                      )
                    }
                    disabled={isSubmitting}
                  >
                    {showConfirmPassword ? (
                      <EyeOff
                        size={18}
                        aria-hidden="true"
                      />
                    ) : (
                      <Eye
                        size={18}
                        aria-hidden="true"
                      />
                    )}
                  </button>
                </div>
              </div>

              {/* Submit */}

              <button
                type="submit"
                className="auth-submit-button"
                disabled={isSubmitting}
                aria-busy={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <Loader2
                      size={18}
                      className="auth-spinner"
                      aria-hidden="true"
                    />

                    Creating account...
                  </>
                ) : (
                  <>
                    Create account

                    <span
                      className="auth-submit-arrow"
                      aria-hidden="true"
                    >
                      →
                    </span>
                  </>
                )}
              </button>
            </form>

            <p className="auth-switch">
              Already have an account?{" "}
              <Link to="/login">Sign in</Link>
            </p>

            <Link
              to="/"
              className="auth-back-link"
            >
              Back to home
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}