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

export function getProjects() {
  return api<Project[]>("/projects");
}

export function createProject(input: CreateProjectRequest) {
  return api<Project>("/projects", {
    method: "POST",
    body: JSON.stringify(input),
  });
}
