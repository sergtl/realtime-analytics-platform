"use client";

import { useProjects } from "@/hooks/use-projects";

export default function ProjectsPage() {
  const { data: projects = [], isPending } = useProjects();

  return (
    <div>
      <h2>Projects</h2>

      {isPending && <span>loading...</span>}

      {!isPending && projects.length === 0 && <span>No projects found</span>}

      {projects?.map((project) => (
        <div key={project.id}>
          <span>{project.name}</span>
        </div>
      ))}
    </div>
  );
}
