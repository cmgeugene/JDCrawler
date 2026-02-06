import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getJobs, toggleBookmark, hideJob } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { Search, MapPin, Building2, Bookmark, ExternalLink, ChevronLeft, ChevronRight, Loader2, Eye, Sparkles, Trash2 } from "lucide-react";
import { JobDetail } from "@/components/jobs/JobDetail";

export default function Jobs() {
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [siteFilter, setSiteFilter] = useState<string>("all");
  const [page, setPage] = useState(1);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const limit = 20;


  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm);
      setPage(1);
    }, 500);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  const { data: jobs, isLoading, isError } = useQuery({
    queryKey: ["jobs", debouncedSearch, siteFilter, page],
    queryFn: () => getJobs({
      q: debouncedSearch || undefined,
      site: siteFilter === "all" ? undefined : siteFilter,
      limit,
      offset: (page - 1) * limit
    }),
  });

  const { mutate: handleToggleBookmark } = useMutation({
    mutationFn: toggleBookmark,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
    },
  });

  const { mutate: handleHideJob } = useMutation({
    mutationFn: hideJob,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
    },
  });

  const handleSiteChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSiteFilter(e.target.value);
    setPage(1);
  };

  return (
    <div className="space-y-6 h-full flex flex-col">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex flex-col gap-1">
          <h1 className="text-3xl font-bold tracking-tight text-primary">Job Listings</h1>
          <p className="text-muted-foreground text-sm font-mono">
            {debouncedSearch ? `Searching for "${debouncedSearch}"` : "Live feed from recruitment channels"}
          </p>
        </div>
        
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by title or company..."
              className="pl-9 bg-card/50 border-input/50 focus:border-primary/50 transition-all"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <Select 
            value={siteFilter} 
            onChange={handleSiteChange}
            className="w-[140px] bg-card/50 border-input/50 focus:border-primary/50"
          >
            <option value="all">All Sites</option>
            <option value="saramin">Saramin</option>
            <option value="jobkorea">Jobkorea</option>
            <option value="wanted">Wanted</option>
          </Select>
        </div>
      </div>

      <div className="rounded-xl border border-border/50 bg-card/30 shadow-sm backdrop-blur-sm flex-1 overflow-hidden flex flex-col">
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-sm text-left">
            <thead className="bg-muted/30 text-xs uppercase font-medium text-muted-foreground/70 sticky top-0 backdrop-blur-md z-10">
              <tr>
                <th className="px-6 py-4 font-mono w-[30%]">Position / Company</th>
                <th className="px-6 py-4 font-mono w-[15%]">Location</th>
                <th className="px-6 py-4 font-mono w-[15%]">Experience</th>
                <th className="px-6 py-4 font-mono w-[15%]">Site</th>
                <th className="px-6 py-4 font-mono w-[15%]">Dates</th>
                <th className="px-6 py-4 font-mono w-[10%] text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/30">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="h-64 text-center">
                    <div className="flex flex-col items-center justify-center gap-2 text-muted-foreground">
                      <Loader2 className="h-8 w-8 animate-spin text-primary" />
                      <span className="font-mono text-xs">Scanning frequencies...</span>
                    </div>
                  </td>
                </tr>
              ) : isError ? (
                <tr>
                  <td colSpan={6} className="h-64 text-center text-destructive font-mono">
                    Connection interrupted. Please retry.
                  </td>
                </tr>
              ) : jobs?.length === 0 ? (
                <tr>
                  <td colSpan={6} className="h-64 text-center text-muted-foreground font-mono">
                    No signals found matching your criteria.
                  </td>
                </tr>
              ) : (
                jobs?.map((job) => (
                  <tr key={job.id} className="group hover:bg-muted/20 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex flex-col gap-1">
                        <div className="flex items-center gap-2">
                          <button 
                            onClick={() => setSelectedJobId(job.id)}
                            className="font-medium text-foreground hover:text-primary transition-colors line-clamp-1 group-hover:underline decoration-primary/50 underline-offset-4 text-left"
                          >
                            {job.title}
                          </button>
                          {job.ai_score !== null && job.ai_score !== undefined && (
                            <span className={cn(
                              "inline-flex items-center gap-0.5 text-[10px] font-bold px-1.5 py-0.5 rounded border font-mono",
                              job.ai_score >= 80 ? "bg-green-500/10 text-green-500 border-green-500/20" :
                              job.ai_score >= 50 ? "bg-yellow-500/10 text-yellow-500 border-yellow-500/20" :
                              "bg-red-500/10 text-red-500 border-red-500/20"
                            )}>
                              <Sparkles className="h-3 w-3" />
                              {job.ai_score}%
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-2 text-muted-foreground text-xs">
                          <Building2 className="h-3 w-3" />
                          <span>{job.company}</span>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-muted-foreground text-xs">
                        <MapPin className="h-3 w-3" />
                        <span className="line-clamp-1">{job.location || "Remote / Unspecified"}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-muted-foreground text-xs font-mono">
                        {job.experience || "N/A"}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={cn(
                        "inline-flex items-center rounded-full px-2 py-1 text-[10px] font-medium ring-1 ring-inset uppercase tracking-wider",
                        job.site === 'saramin' ? "bg-blue-400/10 text-blue-400 ring-blue-400/20" : 
                        job.site === 'jobkorea' ? "bg-indigo-400/10 text-indigo-400 ring-indigo-400/20" :
                        "bg-emerald-400/10 text-emerald-400 ring-emerald-400/20"
                      )}>
                        {job.site}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-muted-foreground text-xs font-mono">
                      <div className="flex flex-col gap-0.5">
                        <span className={cn(
                          "font-medium",
                          job.deadline && (job.deadline.includes("오늘") || job.deadline.includes("내일")) ? "text-red-400" : ""
                        )}>
                          {job.deadline || "Open"}
                        </span>
                        <span className="text-[10px] opacity-70">
                          {job.posted_at ? `Posted: ${job.posted_at}` : ''}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleToggleBookmark(job.id)}
                          className={cn(
                            "h-8 w-8 hover:bg-primary/10 hover:text-primary transition-all",
                            job.is_bookmarked && "text-primary"
                          )}
                        >
                          <Bookmark className={cn("h-4 w-4", job.is_bookmarked && "fill-current")} />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleHideJob(job.id)}
                          className="h-8 w-8 hover:bg-destructive/10 hover:text-destructive transition-all opacity-0 group-hover:opacity-100"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="icon"  
                          onClick={() => setSelectedJobId(job.id)}
                          className="h-8 w-8 hover:bg-muted transition-all opacity-0 group-hover:opacity-100"
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <a href={job.url} target="_blank" rel="noreferrer">
                          <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-muted transition-all opacity-0 group-hover:opacity-100">
                            <ExternalLink className="h-4 w-4" />
                          </Button>
                        </a>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        
        <div className="border-t border-border/50 bg-muted/20 px-6 py-4 flex items-center justify-between">
          <div className="text-xs text-muted-foreground font-mono">
            Page <span className="text-foreground font-bold">{page}</span>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1 || isLoading}
              className="h-8 px-3 border-input/50 hover:bg-background/50 hover:text-primary disabled:opacity-50"
            >
              <ChevronLeft className="h-4 w-4 mr-1" /> Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(p => p + 1)}
              disabled={isLoading || (jobs?.length || 0) < limit}
              className="h-8 px-3 border-input/50 hover:bg-background/50 hover:text-primary disabled:opacity-50"
            >
              Next <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        </div>
      </div>
      
      <JobDetail 
        jobId={selectedJobId} 
        isOpen={!!selectedJobId} 
        onClose={() => setSelectedJobId(null)} 
      />
    </div>
  );
}
