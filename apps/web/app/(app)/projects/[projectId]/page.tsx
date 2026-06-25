"use client";

import Link from "next/link";
import { use, useState } from "react";

import { ErrorAlert } from "@/components/error-alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { useProject, useProjectMetricsOverview } from "@/hooks/use-projects";
import { Activity, FolderKanban, KeyRound, ListFilter } from "lucide-react";
import { ApiKeys } from "@/components/api-keys";

type ProjectDetailPageProps = {
  params: Promise<{
    projectId: string;
  }>;
};

type ProjectSection = "overview" | "events" | "api-keys";

const sections: Array<{
  id: ProjectSection;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}> = [
  { id: "overview", label: "Overview", icon: Activity },
  { id: "events", label: "Events", icon: ListFilter },
  { id: "api-keys", label: "API Keys", icon: KeyRound },
];

function formatDateTime(value: string | null) {
  if (!value) {
    return "No data yet";
  }

  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

function ProjectStatSkeleton() {
  return (
    <Card>
      <CardHeader className="gap-2">
        <Skeleton className="h-3 w-24" />
        <Skeleton className="h-7 w-20" />
      </CardHeader>
    </Card>
  );
}

export default function ProjectDetailPage({ params }: ProjectDetailPageProps) {
  const { projectId } = use(params);

  return <ProjectDetailView projectId={projectId} />;
}

function ProjectDetailView({ projectId }: { projectId: string }) {
  const [activeSection, setActiveSection] =
    useState<ProjectSection>("overview");

  const {
    data: project,
    isPending: isProjectPending,
    error: projectError,
  } = useProject(projectId);

  const {
    data: metrics,
    isPending: isMetricsPending,
    error: metricsError,
  } = useProjectMetricsOverview(projectId);

  if (projectError) {
    return (
      <ErrorAlert
        title="Could not load project"
        description="The dashboard could not fetch this project right now."
      />
    );
  }

  if (!isProjectPending && !project) {
    return (
      <div className="flex flex-col gap-6">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">
            Project
          </p>
          <h1 className="text-2xl font-semibold tracking-tight">
            Project not found
          </h1>
          <p className="max-w-2xl text-sm text-muted-foreground">
            This project either does not exist or is not available in your
            workspace.
          </p>
        </div>

        <Card className="border-dashed">
          <CardContent className="flex min-h-52 flex-col items-center justify-center gap-4 text-center">
            <div className="flex size-12 items-center justify-center rounded-full bg-muted">
              <FolderKanban className="size-5 text-muted-foreground" />
            </div>
            <div className="space-y-1">
              <h2 className="text-sm font-medium">Back to your projects</h2>
              <p className="max-w-md text-sm text-muted-foreground">
                Head back to the projects list and pick another workspace to
                inspect.
              </p>
            </div>
            <Button asChild className="cursor-pointer">
              <Link href="/projects">Open projects</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8">
      <section className="space-y-3">
        <Link
          href="/projects"
          className="text-xs uppercase tracking-[0.18em] text-muted-foreground transition-colors hover:text-foreground"
        >
          Projects
        </Link>

        {isProjectPending || !project ? (
          <div className="space-y-3">
            <Skeleton className="h-8 w-72" />
            <Skeleton className="h-4 w-full max-w-2xl" />
            <Skeleton className="h-4 w-56" />
          </div>
        ) : (
          <div className="space-y-2">
            <h1 className="text-2xl font-semibold tracking-tight">
              {project.name}
            </h1>
            <p className="max-w-2xl text-sm text-muted-foreground">
              Project dashboard for events, metrics, and API key management.
            </p>
            <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted-foreground">
              <span>Slug: {project.slug}</span>
              <span>ID: {project.id}</span>
            </div>
          </div>
        )}
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {isMetricsPending ? (
          <>
            <ProjectStatSkeleton />
            <ProjectStatSkeleton />
            <ProjectStatSkeleton />
            <ProjectStatSkeleton />
          </>
        ) : metricsError ? (
          <div className="md:col-span-2 xl:col-span-4">
            <ErrorAlert
              title="Could not load overview metrics"
              description="The project loaded, but its summary metrics are unavailable right now."
            />
          </div>
        ) : (
          <>
            <Card>
              <CardHeader>
                <CardDescription>Total events</CardDescription>
                <CardTitle className="text-2xl">
                  {metrics?.total_events ?? 0}
                </CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <CardDescription>Unique event types</CardDescription>
                <CardTitle className="text-2xl">
                  {metrics?.unique_event_types ?? 0}
                </CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <CardDescription>First event</CardDescription>
                <CardTitle className="text-base font-medium">
                  {formatDateTime(metrics?.first_event_at ?? null)}
                </CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <CardDescription>Latest event</CardDescription>
                <CardTitle className="text-base font-medium">
                  {formatDateTime(metrics?.latest_event_at ?? null)}
                </CardTitle>
              </CardHeader>
            </Card>
          </>
        )}
      </section>

      <section className="flex flex-wrap gap-2 border-b pb-3">
        {sections.map((section) => {
          const Icon = section.icon;

          return (
            <button
              key={section.id}
              type="button"
              className={cn(
                "inline-flex h-8 items-center gap-2 border px-3 text-sm transition-colors",
                activeSection === section.id
                  ? "border-foreground bg-foreground text-background"
                  : "border-border bg-background text-foreground hover:bg-muted",
              )}
              onClick={() => setActiveSection(section.id)}
            >
              <Icon className="size-4" />
              <span>{section.label}</span>
            </button>
          );
        })}
      </section>

      {activeSection === "overview" ? (
        <section className="grid gap-6 xl:grid-cols-[minmax(0,1.5fr)_minmax(320px,0.9fr)]">
          <Card>
            <CardHeader>
              <CardTitle>Overview</CardTitle>
              <CardDescription>
                This is the landing area for the project. Next we&apos;ll plug
                in the timeseries chart and higher-level usage patterns here.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-muted-foreground">
              <p>
                The top summary cards are already live, so this page can act as
                the project home even before deeper analytics views are filled
                in.
              </p>
              <p>
                The next natural additions here are event volume over time, top
                event types, and a short list of recent activity.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>What you&apos;ll manage here</CardTitle>
              <CardDescription>
                The project page is where the product loop comes together.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              <p>1. Generate API keys for this project.</p>
              <p>2. Connect your app or SDK to start sending events.</p>
              <p>3. Inspect raw event traffic as soon as it arrives.</p>
              <p>4. Watch metrics become useful as data accumulates.</p>
            </CardContent>
          </Card>
        </section>
      ) : null}

      {activeSection === "events" ? (
        <section>
          <Card>
            <CardHeader>
              <CardTitle>Events</CardTitle>
              <CardDescription>
                This section will show recent project events, filters, and
                event-type summaries.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              <p>
                The backend endpoints are ready for recent events and event
                types, so the next UI step here is a table with basic filters
                and pagination.
              </p>
            </CardContent>
          </Card>
        </section>
      ) : null}

      {activeSection === "api-keys" ? <ApiKeys projectId={projectId} /> : null}
    </div>
  );
}
