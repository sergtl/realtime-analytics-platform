"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { ErrorAlert } from "@/components/error-alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { useCreateProject, useProjects } from "@/hooks/use-projects";
import { FolderKanban } from "lucide-react";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

export default function ProjectsPage() {
  const router = useRouter();
  const [projectName, setProjectName] = useState("");

  const {
    data: projects = [],
    isPending: isProjectsPending,
    error: projectsError,
  } = useProjects();

  const {
    mutate: createProject,
    isPending: isCreatingProject,
    error: createProjectError,
  } = useCreateProject({
    onSuccess: (project) => {
      setProjectName("");
      router.push(`/projects/${project.id}`);
    },
  });

  function onSubmit(event: React.SubmitEvent<HTMLFormElement>) {
    event.preventDefault();

    createProject({
      name: projectName.trim(),
    });
  }

  return (
    <div className="flex flex-col gap-8">
      <section className="flex flex-col gap-2">
        <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">
          Workspace
        </p>
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight">Projects</h1>
          <p className="max-w-2xl text-sm text-muted-foreground">
            Create a project, generate an API key, and start tracking product
            events from your app.
          </p>
        </div>
      </section>

      <section>
        <Card>
          <CardHeader>
            <CardTitle>Create a project</CardTitle>
            <CardDescription>
              Each project gets its own events, metrics, and API keys.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={onSubmit}>
              <FieldGroup>
                {createProjectError ? (
                  <ErrorAlert
                    title="Could not create project"
                    description="Please try again. If the problem persists, check the API and try one more time."
                  />
                ) : null}

                <Field>
                  <FieldLabel htmlFor="project-name">Project name</FieldLabel>
                  <Input
                    id="project-name"
                    value={projectName}
                    disabled={isCreatingProject}
                    placeholder="Your project name"
                    onChange={(event) => setProjectName(event.target.value)}
                    required
                  />
                  <FieldDescription>
                    We&apos;ll generate a unique slug for the project
                    automatically.
                  </FieldDescription>
                </Field>

                <Field>
                  <div className="flex gap-3">
                    <Button
                      type="submit"
                      disabled={isCreatingProject || projectName.trim() === ""}
                      className="cursor-pointer"
                    >
                      {isCreatingProject ? "Creating..." : "Create project"}
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      disabled={isCreatingProject || projectName === ""}
                      className="cursor-pointer"
                      onClick={() => setProjectName("")}
                    >
                      Clear
                    </Button>
                  </div>
                </Field>
              </FieldGroup>
            </form>
          </CardContent>
        </Card>
      </section>

      <section className="flex flex-col gap-4">
        <div className="space-y-1">
          <h2 className="text-lg font-medium">Your projects</h2>
          <p className="text-sm text-muted-foreground">
            Pick a project to inspect events, metrics, and API keys.
          </p>
        </div>

        {projectsError ? (
          <ErrorAlert
            title="Could not load projects"
            description="The dashboard could not fetch your projects right now."
          />
        ) : null}

        {isProjectsPending ? (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {Array.from({ length: 3 }).map((_, index) => (
              <Card key={index} className="min-h-40 animate-pulse" />
            ))}
          </div>
        ) : null}

        {!isProjectsPending && projects.length === 0 ? (
          <Card className="border-dashed">
            <CardContent className="flex min-h-52 flex-col items-center justify-center gap-4 text-center">
              <div className="flex size-12 items-center justify-center rounded-full bg-muted">
                <FolderKanban className="size-5 text-muted-foreground" />
              </div>
              <div className="space-y-1">
                <h3 className="text-sm font-medium">No projects yet</h3>
                <p className="max-w-md text-sm text-muted-foreground">
                  Create your first project to start collecting events and
                  building out your analytics dashboard.
                </p>
              </div>
            </CardContent>
          </Card>
        ) : null}

        {!isProjectsPending && projects.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {projects.map((project) => (
              <Link key={project.id} href={`/projects/${project.id}`}>
                <Card className="min-h-44 cursor-pointer transition-colors hover:bg-muted/35">
                  <CardHeader>
                    <CardTitle>{project.name}</CardTitle>
                    <CardDescription>{project.slug}</CardDescription>
                  </CardHeader>
                  <CardContent className="flex h-full flex-col justify-end gap-3">
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>Created {formatDate(project.created_at)}</span>
                      <span>Open project</span>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        ) : null}

        <Card className="border-dashed">
          <CardHeader>
            <CardTitle>What happens next</CardTitle>
            <CardDescription>
              The first useful loop is short and practical.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            <p>1. Create a project.</p>
            <p>2. Generate an API key for that project.</p>
            <p>3. Add the SDK or tracking snippet to your product.</p>
            <p>4. Return here to explore metrics and raw events.</p>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
