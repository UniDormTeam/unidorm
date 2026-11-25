
/*موقت تا کوکی*/
import type { LoginResponse, Organization } from "../types/user";

const AUTH_STORAGE_KEY = "unidorm_auth";

export type AuthSession = LoginResponse;

export function saveAuthSession(data: LoginResponse): void {
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(data));
}

export function getAuthSession(): AuthSession | null {
  const storedData = localStorage.getItem(AUTH_STORAGE_KEY);

  if (!storedData) return null;

  try {
    return JSON.parse(storedData) as AuthSession;
  } catch {
    localStorage.removeItem(AUTH_STORAGE_KEY);
    return null;
  }
}

export function getAccessToken(): string | null {
  return getAuthSession()?.tokens.access ?? null;
}

export function getRefreshToken(): string | null {
  return getAuthSession()?.tokens.refresh ?? null;
}

export function updateAccessToken(access: string): void {
  const session = getAuthSession();

  if (!session) return;

  saveAuthSession({
    ...session,
    tokens: {
      ...session.tokens,
      access,
    },
  });
}

export function getDefaultOrganization(): Organization | null {
  const session = getAuthSession();

  if (!session) return null;

  return (
    session.organizations.find((organization) => organization.is_default) ??
    session.organizations[0] ??
    null
  );
}

export function clearAuthSession(): void {
  localStorage.removeItem(AUTH_STORAGE_KEY);
}