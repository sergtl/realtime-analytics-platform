import {
  createApiKey,
  CreateApiKeyRequest,
  CreateApiKeyResponse,
  getApiKeys,
  revokeApiKey,
  ApiKey,
} from "@/lib/api/projects";
import {
  useMutation,
  UseMutationOptions,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

export function useApiKeys(projectId: string) {
  return useQuery({
    queryKey: [projectId, "api-keys"],
    queryFn: () => getApiKeys(projectId),
  });
}

type CreateApiKeyHookOptions = UseMutationOptions<
  CreateApiKeyResponse,
  Error,
  CreateApiKeyRequest,
  unknown
>;

export function useCreateApiKey(
  projectId: string,
  options?: CreateApiKeyHookOptions
) {
  const queryClient = useQueryClient();
  const { onSuccess, ...restOptions } = options ?? {};

  return useMutation({
    mutationFn: (input: CreateApiKeyRequest) => createApiKey(projectId, input),
    onSuccess: (...args) => {
      void queryClient.invalidateQueries({ queryKey: [projectId, "api-keys"] });
      onSuccess?.(...args);
    },
    ...restOptions,
  });
}

type RevokeApiKeyHookOptions = UseMutationOptions<
  ApiKey,
  Error,
  string,
  unknown
>;

export function useRevokeApiKey(
  projectId: string,
  options?: RevokeApiKeyHookOptions
) {
  const queryClient = useQueryClient();
  const { onSuccess, ...restOptions } = options ?? {};

  return useMutation({
    mutationFn: (apiKeyId: string) => revokeApiKey(projectId, apiKeyId),
    onSuccess: (...args) => {
      void queryClient.invalidateQueries({ queryKey: [projectId, "api-keys"] });
      onSuccess?.(...args);
    },
    ...restOptions,
  });
}
