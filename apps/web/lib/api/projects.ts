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

export type ApiKey = {
  id: string;
  name: string;
  prefix: string;
  created_at: string;
  last_used_at: string | null;
  revoked_at: string | null;
};

export type CreateApiKeyRequest = {
  name: string;
};

export type CreateApiKeyResponse = {
  api_key: ApiKey;
  raw_key: string;
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

export function getApiKeys(projectId: string) {
  return api<ApiKey[]>(`/projects/${projectId}/api-keys`);
}

export function createApiKey(projectId: string, input: CreateApiKeyRequest) {
  return api<CreateApiKeyResponse>(`/projects/${projectId}/api-keys`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function revokeApiKey(projectId: string, apiKeyId: string) {
  return api<ApiKey>(`/projects/${projectId}/api-keys/${apiKeyId}/revoke`, {
    method: "POST",
  });
}
