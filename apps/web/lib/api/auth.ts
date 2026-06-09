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

export function register(input: AuthenticateRequest) {
  return api<AuthUser>("/auth/register", {
    method: "POST",
    body: JSON.stringify(input),
  });
}
