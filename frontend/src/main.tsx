import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./index.css";

import App from "./App";
import { AuthProvider } from "./context/AuthContext";

/* ==========================================================================
   Application Bootstrap
   ========================================================================== */

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error(
    "Application root element was not found.",
  );
}

createRoot(rootElement).render(
  <StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </StrictMode>,
);