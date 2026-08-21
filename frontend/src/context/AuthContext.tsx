import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";

import {
  getCurrentUser,
  login as loginRequest,
  logout as logoutRequest,
  register as registerRequest,
  tokenStorage,
  type LoginRequest,
  type RegisterRequest,
  type TokenResponse,
  type User,
} from "../services/api";

/* ==========================================================================
   Types
   ========================================================================== */

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  login: (
    credentials: LoginRequest,
  ) => Promise<TokenResponse>;

  register: (
    data: RegisterRequest,
  ) => Promise<User>;

  logout: () => Promise<void>;

  refreshUser: () => Promise<User | null>;
}

interface AuthProviderProps {
  children: ReactNode;
}

/* ==========================================================================
   Context
   ========================================================================== */

const AuthContext =
  createContext<AuthContextValue | undefined>(
    undefined,
  );

/* ==========================================================================
   Auth Provider
   ========================================================================== */

export function AuthProvider({
  children,
}: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(
    null,
  );

  const [isLoading, setIsLoading] =
    useState<boolean>(true);

  /*
   * Prevents state updates after the provider has
   * already been unmounted.
   */
  const mountedRef = useRef(true);

  /* ------------------------------------------------------------------------
     Mount / unmount tracking
     ------------------------------------------------------------------------ */

  useEffect(() => {
    mountedRef.current = true;

    return () => {
      mountedRef.current = false;
    };
  }, []);

  /* ------------------------------------------------------------------------
     Clear authentication
     ------------------------------------------------------------------------ */

  const clearAuthentication = useCallback(() => {
    tokenStorage.clear();

    if (mountedRef.current) {
      setUser(null);
    }
  }, []);

  /* ------------------------------------------------------------------------
     Refresh current user
     ------------------------------------------------------------------------ */

  const refreshUser = useCallback(
    async (): Promise<User | null> => {
      const token = tokenStorage.get();

      /*
       * No access token means the user is definitely
       * unauthenticated.
       */
      if (!token) {
        if (mountedRef.current) {
          setUser(null);
        }

        return null;
      }

      try {
        const currentUser =
          await getCurrentUser();

        if (mountedRef.current) {
          setUser(currentUser);
        }

        return currentUser;
      } catch {
        /*
         * The token may be expired, revoked, malformed,
         * or otherwise invalid.
         */
        clearAuthentication();

        return null;
      }
    },
    [clearAuthentication],
  );

  /* ------------------------------------------------------------------------
     Initial authentication bootstrap
     ------------------------------------------------------------------------ */

  useEffect(() => {
    let cancelled = false;

    const initialize = async () => {
      const token = tokenStorage.get();

      /*
       * No token:
       * authentication initialization is complete.
       */
      if (!token) {
        if (!cancelled && mountedRef.current) {
          setUser(null);
          setIsLoading(false);
        }

        return;
      }

      try {
        const currentUser =
          await getCurrentUser();

        if (
          !cancelled &&
          mountedRef.current
        ) {
          setUser(currentUser);
        }
      } catch {
        /*
         * Invalid/expired token.
         */
        tokenStorage.clear();

        if (
          !cancelled &&
          mountedRef.current
        ) {
          setUser(null);
        }
      } finally {
        if (
          !cancelled &&
          mountedRef.current
        ) {
          setIsLoading(false);
        }
      }
    };

    void initialize();

    return () => {
      cancelled = true;
    };
  }, []);

  /* ------------------------------------------------------------------------
     Login
     ------------------------------------------------------------------------ */

  const login = useCallback(
    async (
      credentials: LoginRequest,
    ): Promise<TokenResponse> => {
      /*
       * api.ts stores the access token after a
       * successful login request.
       */
      const tokenResponse =
        await loginRequest(credentials);

      try {
        /*
         * Resolve the complete authenticated user
         * immediately after receiving the token.
         */
        const currentUser =
          await getCurrentUser();

        if (mountedRef.current) {
          setUser(currentUser);
        }
      } catch (error) {
        /*
         * Never leave a token behind if we cannot
         * establish the authenticated user session.
         */
        clearAuthentication();

        throw error;
      }

      return tokenResponse;
    },
    [clearAuthentication],
  );

  /* ------------------------------------------------------------------------
     Registration
     ------------------------------------------------------------------------ */

  const register = useCallback(
    async (
      data: RegisterRequest,
    ): Promise<User> => {
      return registerRequest(data);
    },
    [],
  );

  /* ------------------------------------------------------------------------
     Logout
     ------------------------------------------------------------------------ */

  const logout = useCallback(
    async (): Promise<void> => {
      try {
        await logoutRequest();
      } finally {
        /*
         * Always clear local authentication state,
         * even if the backend logout request fails.
         */
        clearAuthentication();
      }
    },
    [clearAuthentication],
  );

  /* ------------------------------------------------------------------------
     Derived authentication state
     ------------------------------------------------------------------------ */

  const isAuthenticated =
    !isLoading && user !== null;

  /* ------------------------------------------------------------------------
     Context value
     ------------------------------------------------------------------------ */

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated,
      isLoading,
      login,
      register,
      logout,
      refreshUser,
    }),
    [
      user,
      isAuthenticated,
      isLoading,
      login,
      register,
      logout,
      refreshUser,
    ],
  );

  /* ------------------------------------------------------------------------
     Provider
     ------------------------------------------------------------------------ */

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

/* ==========================================================================
   Hook
   ========================================================================== */

export function useAuth(): AuthContextValue {
  const context =
    useContext(AuthContext);

  if (context === undefined) {
    throw new Error(
      "useAuth must be used inside an AuthProvider.",
    );
  }

  return context;
}

export default AuthContext;