"use client";

import { AppSidebar } from "@/components/app-sidebar";
import { useMe } from "@/hooks/use-me";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function AppRootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const router = useRouter();
  const { data: user, isLoading, isError } = useMe();

  useEffect(() => {
    if (isError) {
      router.replace("/login");
    }
  }, [isError, router]);

  if (isLoading) {
    return <span>loading... please stand by.</span>;
  }

  if (!user) {
    return null;
  }

  return (
    <div className="flex h-svh bg-background text-foreground">
      <aside className="h-svh w-64 shrink-0 border-r bg-sidebar text-sidebar-foreground">
        <AppSidebar />
      </aside>

      <main className="min-w-0 flex-1 overflow-y-auto">
        <div className="mx-auto w-full max-w-7xl px-6 py-6">{children}</div>
      </main>
    </div>
  );
}
