import { api } from "./client";

export type Project = {
  id: string;
  name: string;
  slug: string;
  created_at: string;
  updated_at: string;
};

export type CreateProjectRequest = {
  name: string;
};

export type ProjectMetricsOverview = {
  total_events: number;
  unique_event_types: number;
  first_event_at: string | null;
  latest_event_at: string | null;
};

export function getProject(projectId: string) {
  return api<Project>(`/projects/${projectId}`);
}

export function getProjects() {
  return api<Project[]>("/projects");
}

export function createProject(input: CreateProjectRequest) {
  return api<Project>("/projects", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function getProjectMetricsOverview(projectId: string) {
  return api<ProjectMetricsOverview>(`/projects/${projectId}/metrics/overview`);
}
