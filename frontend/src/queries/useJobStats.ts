import { useQuery } from "@tanstack/react-query";
import { getJobStats } from "@/lib/api";

export function useJobStats() {
    return useQuery({
        queryKey: ["jobStats"],
        queryFn: getJobStats,
    });
}
