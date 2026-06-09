import { api } from "./client";

export type AuthenticateRequest = {
  email: string;
  password: string;
};

export type AuthUser = {
  id: number;
  email: string;
};

export function login(input: AuthenticateRequest) {
  return api<AuthUser>("/auth/login", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export type LogoutResponse = {
  ok: boolean;
};

export function logout() {
  return api<LogoutResponse>("/auth/logout", {
    method: "POST",
  });
}

export function register(input: AuthenticateRequest) {
  return api<AuthUser>("/auth/register", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function me() {
  return api<AuthUser>("/auth/me");
}
