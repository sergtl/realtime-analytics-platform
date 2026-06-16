type ProjectDetailPageProps = {
  params: Promise<{
    projectId: string;
  }>;
};

export default async function ProjectDetailPage({
  params,
}: ProjectDetailPageProps) {
  const { projectId } = await params;

  return (
    <div className="flex flex-col gap-3">
      <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">
        Project
      </p>
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">
          Project dashboard
        </h1>
        <p className="text-sm text-muted-foreground">
          We&apos;ll flesh this page out next with overview metrics, timeseries,
          event types, recent events, and API key management.
        </p>
      </div>
      <div className="rounded-none border border-dashed p-6 text-sm text-muted-foreground">
        Project ID: {projectId}
      </div>
    </div>
  );
}
