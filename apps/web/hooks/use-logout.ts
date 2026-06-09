import { logout, LogoutResponse } from "@/lib/api/auth";
import { useMutation, UseMutationOptions } from "@tanstack/react-query";

type LogoutHookOptions = UseMutationOptions<
  LogoutResponse,
  Error,
  void,
  unknown
>;

export function useLogout(options?: LogoutHookOptions) {
  return useMutation({
    mutationFn: logout,
    ...options,
  });
}
