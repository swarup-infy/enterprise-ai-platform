import {
  BrowserRouter,
  Link,
  Navigate,
  Outlet,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";
import {
  ArrowRight,
  FileText,
  LoaderCircle,
  ShieldAlert,
} from "lucide-react";
import type { ReactNode } from "react";

import "./App.css";

import { useAuth } from "./context/AuthContext";

import ChatPage from "./pages/ChatPage";
import DashboardPage from "./pages/DashboardPage";
import DocumentsPage from "./pages/DocumentsPage";
import LoginPage from "./pages/auth/LoginPage";
import RegisterPage from "./pages/auth/RegisterPage";

/* ==========================================================================
   Types
   ========================================================================== */

interface RouteGuardProps {
  children?: ReactNode;
}

/* ==========================================================================
   Loading screen
   ========================================================================== */

function AppLoading({
  message = "Preparing your workspace...",
}: {
  message?: string;
}) {
  return (
    <main
      className="app-loading"
      aria-live="polite"
      aria-busy="true"
    >
      <div
        className="app-loading-glow"
        aria-hidden="true"
      />

      <div className="app-loading-content">
        <div className="app-loading-icon">
          <LoaderCircle
            className="app-loading-spinner"
            size={36}
            strokeWidth={1.7}
            aria-hidden="true"
          />
        </div>

        <strong>{message}</strong>

        <span>
          Verifying your secure session
        </span>
      </div>
    </main>
  );
}

/* ==========================================================================
   Protected route
   ========================================================================== */

function ProtectedRoute({
  children,
}: RouteGuardProps) {
  const {
    isAuthenticated,
    isLoading,
  } = useAuth();

  const location = useLocation();

  if (isLoading) {
    return <AppLoading />;
  }

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
        state={{
          from: `${location.pathname}${location.search}${location.hash}`,
        }}
      />
    );
  }

  return <>{children}</>;
}

/* ==========================================================================
   Public-only route
   ========================================================================== */

function PublicRoute({
  children,
}: RouteGuardProps) {
  const {
    isAuthenticated,
    isLoading,
  } = useAuth();

  if (isLoading) {
    return (
      <AppLoading
        message="Loading Enterprise AI..."
      />
    );
  }

  if (isAuthenticated) {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    );
  }

  return <>{children}</>;
}

/* ==========================================================================
   Protected layout
   ========================================================================== */

function ProtectedLayout() {
  return (
    <ProtectedRoute>
      <Outlet />
    </ProtectedRoute>
  );
}

/* ==========================================================================
   Home page
   ========================================================================== */

function HomePage() {
  return (
    <main className="app-shell">
      <section className="landing-page">
        <div
          className="landing-background"
          aria-hidden="true"
        >
          <div className="landing-grid" />

          <div className="landing-orb landing-orb-one" />

          <div className="landing-orb landing-orb-two" />
        </div>

        <nav className="landing-nav">
          <Link
            to="/"
            className="landing-brand"
            aria-label="Enterprise AI home"
          >
            <span className="landing-brand-icon">
              <FileText
                size={19}
                strokeWidth={2.2}
                aria-hidden="true"
              />
            </span>

            <span>Enterprise AI</span>
          </Link>

          <div className="landing-nav-actions">
            <Link
              to="/login"
              className="landing-nav-login"
            >
              Sign in
            </Link>

            <Link
              to="/register"
              className="landing-nav-register"
            >
              Get started
            </Link>
          </div>
        </nav>

        <div className="landing-content">
          <span className="landing-badge">
            <span
              className="landing-badge-dot"
              aria-hidden="true"
            />

            Enterprise AI Platform
          </span>

          <h1>
            Your documents.
            <br />

            <span>Smarter with AI.</span>
          </h1>

          <p>
            Upload documents, understand their content,
            search your knowledge, and have intelligent
            conversations with your data.
          </p>

          <div className="landing-actions">
            <Link
              to="/login"
              className="primary-button"
            >
              Sign in

              <ArrowRight
                size={17}
                aria-hidden="true"
              />
            </Link>

            <Link
              to="/register"
              className="secondary-button"
            >
              Create account
            </Link>
          </div>

          <div className="landing-trust">
            <span>
              Secure document-aware AI
            </span>

            <span
              className="landing-trust-separator"
              aria-hidden="true"
            >
              •
            </span>

            <span>
              Private knowledge base
            </span>

            <span
              className="landing-trust-separator"
              aria-hidden="true"
            >
              •
            </span>

            <span>
              RAG-powered conversations
            </span>
          </div>
        </div>

        <div className="landing-scroll-hint">
          <span />
          Built for intelligent work
        </div>
      </section>
    </main>
  );
}

/* ==========================================================================
   Profile
   ========================================================================== */

function ProfilePage() {
  const { user } = useAuth();

  const displayName =
    user?.username ||
    user?.email?.split("@")[0] ||
    "Profile";

  return (
    <main className="app-shell">
      <section className="placeholder-page">
        <div className="placeholder-card">
          <span className="landing-badge">
            Account
          </span>

          <h1>{displayName}</h1>

          <p>
            Manage your account settings and personal
            information.
          </p>

          {user?.email && (
            <p>{user.email}</p>
          )}

          <Link
            to="/dashboard"
            className="primary-button"
          >
            Back to dashboard

            <ArrowRight
              size={17}
              aria-hidden="true"
            />
          </Link>
        </div>
      </section>
    </main>
  );
}

/* ==========================================================================
   Not found
   ========================================================================== */

function NotFoundPage() {
  return (
    <main className="app-shell">
      <section className="placeholder-page">
        <div className="placeholder-card">
          <span className="landing-badge">
            <ShieldAlert
              size={14}
              aria-hidden="true"
            />

            404
          </span>

          <h1>Page not found</h1>

          <p>
            The page you&apos;re looking for doesn&apos;t
            exist or may have been moved.
          </p>

          <Link
            to="/"
            className="primary-button"
          >
            Back to home

            <ArrowRight
              size={17}
              aria-hidden="true"
            />
          </Link>
        </div>
      </section>
    </main>
  );
}

/* ==========================================================================
   Application
   ========================================================================== */

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ==================================================================
            Public
            ================================================================== */}

        <Route
          path="/"
          element={<HomePage />}
        />

        <Route
          path="/login"
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          }
        />

        <Route
          path="/register"
          element={
            <PublicRoute>
              <RegisterPage />
            </PublicRoute>
          }
        />

        {/* ==================================================================
            Protected application
            ================================================================== */}

        <Route element={<ProtectedLayout />}>
          <Route
            path="/dashboard"
            element={<DashboardPage />}
          />

          <Route
            path="/documents"
            element={<DocumentsPage />}
          />

          <Route
            path="/chat"
            element={<ChatPage />}
          />

          <Route
            path="/profile"
            element={<ProfilePage />}
          />
        </Route>

        {/* ==================================================================
            404
            ================================================================== */}

        <Route
          path="/404"
          element={<NotFoundPage />}
        />

        <Route
          path="*"
          element={
            <Navigate
              to="/404"
              replace
            />
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;