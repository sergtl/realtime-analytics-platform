"use client";

import { AppSidebar } from "@/components/app-sidebar";
import { CreateProjectSheet } from "@/components/create-project-sheet";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { useMe } from "@/hooks/use-me";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function AppRootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const router = useRouter();
  const [isCreateProjectOpen, setIsCreateProjectOpen] = useState(false);
  const { data: user, isLoading, isError } = useMe();

  useEffect(() => {
    if (isError) {
      async function clearSessionAndRedirect() {
        await fetch("/api/auth/session", {
          method: "DELETE",
        });

        router.replace("/login");
      }

      void clearSessionAndRedirect();
    }
  }, [isError, router]);

  if (isLoading) {
    return <span>loading... please stand by.</span>;
  }

  if (!user) {
    return null;
  }

  return (
    <SidebarProvider>
      <AppSidebar onCreateProjectClick={() => setIsCreateProjectOpen(true)} />
      <CreateProjectSheet
        open={isCreateProjectOpen}
        onOpenChange={setIsCreateProjectOpen}
      />

      <SidebarInset>
        <header className="flex h-12 items-center px-4">
          <SidebarTrigger size="xs" />
        </header>

        <main className="min-w-0 flex-1 overflow-y-auto">
          <div className="mx-auto w-full max-w-7xl px-6 py-6">{children}</div>
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
}
