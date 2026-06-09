import { AuthenticateRequest, AuthUser, login } from "@/lib/api/auth";
import { useMutation, UseMutationOptions } from "@tanstack/react-query";

type LoginHookOptions = UseMutationOptions<
  AuthUser,
  Error,
  AuthenticateRequest,
  unknown
>;

export function useLogin(options?: LoginHookOptions) {
  return useMutation({
    mutationFn: login,
    ...options,
  });
}
