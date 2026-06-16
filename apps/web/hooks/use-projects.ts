import {
  createProject,
  getProjects,
  Project,
  CreateProjectRequest,
} from "@/lib/api/projects";
import {
  useMutation,
  UseMutationOptions,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

export function useProjects() {
  return useQuery({
    queryKey: ["projects"],
    queryFn: getProjects,
  });
}

type CreateProjectHookOptions = UseMutationOptions<
  Project,
  Error,
  CreateProjectRequest,
  unknown
>;

export function useCreateProject(options?: CreateProjectHookOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createProject,
    onSuccess: (...args) => {
      void queryClient.invalidateQueries({ queryKey: ["projects"] });
      options?.onSuccess?.(...args);
    },
    ...options,
  });
}
