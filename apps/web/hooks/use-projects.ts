import {
  createProject,
  CreateProjectRequest,
  getProject,
  getProjectMetricsOverview,
  getProjects,
  Project,
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

export function useProject(projectId: string) {
  return useQuery({
    queryKey: ["projects", projectId],
    queryFn: () => getProject(projectId),
  });
}

export function useProjectMetricsOverview(projectId: string) {
  return useQuery({
    queryKey: ["projects", projectId, "metrics-overview"],
    queryFn: () => getProjectMetricsOverview(projectId),
    enabled: projectId.length > 0,
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
