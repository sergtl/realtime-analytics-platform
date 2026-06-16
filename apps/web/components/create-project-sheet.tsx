"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { ErrorAlert } from "@/components/error-alert";
import { Button } from "@/components/ui/button";
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { useCreateProject } from "@/hooks/use-projects";

type CreateProjectSheetProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

export function CreateProjectSheet({
  open,
  onOpenChange,
}: CreateProjectSheetProps) {
  const router = useRouter();
  const [projectName, setProjectName] = useState("");

  const {
    mutate: createProject,
    isPending: isCreatingProject,
    error: createProjectError,
  } = useCreateProject({
    onSuccess: (project) => {
      setProjectName("");
      onOpenChange(false);

      toast.success(`Created ${project.name}.`, {
        action: {
          label: "Open project",
          onClick: () => router.push(`/projects/${project.id}`),
        },
      });
    },
  });

  function onSubmit(event: React.SubmitEvent<HTMLFormElement>) {
    event.preventDefault();

    createProject({
      name: projectName.trim(),
    });
  }

  function onSheetOpenChange(nextOpen: boolean) {
    onOpenChange(nextOpen);

    if (!nextOpen) {
      setProjectName("");
    }
  }

  return (
    <Sheet open={open} onOpenChange={onSheetOpenChange}>
      <SheetContent side="left" className="w-full sm:max-w-md">
        <SheetHeader>
          <SheetTitle>Create project</SheetTitle>
          <SheetDescription>
            Add a project once, then manage events, metrics, and API keys from
            anywhere in the dashboard.
          </SheetDescription>
        </SheetHeader>

        <form onSubmit={onSubmit} className="flex flex-1 flex-col px-4 pb-4">
          <FieldGroup className="flex-1">
            {createProjectError ? (
              <ErrorAlert
                title="Could not create project"
                description="Please try again. If the problem persists, check the API and try one more time."
              />
            ) : null}

            <Field>
              <FieldLabel htmlFor="sheet-project-name">Project name</FieldLabel>
              <Input
                id="sheet-project-name"
                value={projectName}
                disabled={isCreatingProject}
                placeholder="Your project name"
                onChange={(event) => setProjectName(event.target.value)}
                required
                autoFocus
              />
              <FieldDescription>
                We&apos;ll generate a unique slug for the project automatically.
              </FieldDescription>
            </Field>
          </FieldGroup>

          <div className="mt-6 flex gap-3">
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
        </form>
      </SheetContent>
    </Sheet>
  );
}
