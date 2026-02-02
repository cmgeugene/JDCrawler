import { useQuery } from "@tanstack/react-query";
import { getNewJobsCount } from "@/lib/api";

export function useNewJobsCount() {
    return useQuery({
        queryKey: ["newJobsCount"],
        queryFn: getNewJobsCount,
        refetchInterval: 60000,
    });
}
