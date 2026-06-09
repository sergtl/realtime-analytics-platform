import { api } from "./client";

type Project = {
  id: string;
  name: string;
  slug: string;
  created_at: Date;
  updated_at: Date;
};

export function getProjects() {
  return api<Project[]>("/projects");
}
