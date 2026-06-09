import { AuthenticateRequest, AuthUser, register } from "@/lib/api/auth";
import { useMutation, UseMutationOptions } from "@tanstack/react-query";

type RegisterHookOptions = UseMutationOptions<
  AuthUser,
  Error,
  AuthenticateRequest,
  unknown
>;

export function useRegister(options?: RegisterHookOptions) {
  return useMutation({
    mutationFn: register,
    ...options,
  });
}
