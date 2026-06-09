import { me } from "@/lib/api/auth";
import { useQuery } from "@tanstack/react-query";

export function useMe() {
  return useQuery({
    queryKey: ["me"],
    queryFn: me,
  });
}
