"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

type TanstackProviderProps = {
  children: React.ReactNode;
};

const queryClient = new QueryClient();

export function TanstackProvider({ children }: TanstackProviderProps) {
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
