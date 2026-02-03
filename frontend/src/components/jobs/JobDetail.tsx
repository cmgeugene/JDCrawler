import { useEffect } from "react";
import { createPortal } from "react-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { X, Building2, MapPin, Calendar, ExternalLink, Bookmark, Globe, Loader2, DollarSign, Sparkles, BrainCircuit, CheckCircle2, AlertCircle } from "lucide-react";
import { getJob, toggleBookmark, analyzeJob } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface JobDetailProps {
  jobId: number | null;
  isOpen: boolean;
  onClose: () => void;
}

export function JobDetail({ jobId, isOpen, onClose }: JobDetailProps) {
  const queryClient = useQueryClient();

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      document.addEventListener("keydown", handleEsc);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleEsc);
      document.body.style.overflow = "unset";
    };
  }, [isOpen, onClose]);

  const { data: job, isLoading, isError } = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => (jobId ? getJob(jobId) : Promise.resolve(null)),
    enabled: !!jobId && isOpen,
  });

  const { mutate: handleToggleBookmark } = useMutation({
    mutationFn: toggleBookmark,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["job", jobId] });
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
    },
  });

  const { mutate: handleAnalyze, isPending: isAnalyzing } = useMutation({
    mutationFn: () => analyzeJob(jobId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["job", jobId] });
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
    },
  });

  if (!isOpen) return null;

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center sm:items-center sm:justify-center">
      <div 
        className="fixed inset-0 bg-background/80 backdrop-blur-sm transition-all duration-100"
        onClick={onClose}
      />
      
      <div className="relative z-50 w-full max-w-2xl gap-4 border border-border/50 bg-card p-0 shadow-lg sm:rounded-xl overflow-hidden animate-in fade-in zoom-in-95 duration-200 mx-4 max-h-[90vh] flex flex-col">
        
        <div className="flex items-center justify-between border-b border-border/50 px-6 py-4 bg-muted/20">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
            <h2 className="text-sm font-mono uppercase tracking-widest text-muted-foreground">
              Job Details
            </h2>
          </div>
          <Button 
            variant="ghost" 
            size="icon" 
            className="h-8 w-8 rounded-full hover:bg-background/50" 
            onClick={onClose}
          >
            <X className="h-4 w-4" />
            <span className="sr-only">Close</span>
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent">
          {isLoading ? (
            <div className="flex h-40 flex-col items-center justify-center gap-4">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <p className="font-mono text-sm text-muted-foreground">Retrieving data...</p>
            </div>
          ) : isError ? (
            <div className="flex h-40 flex-col items-center justify-center gap-4 text-destructive">
              <p>Failed to load job details</p>
            </div>
          ) : job ? (
            <div className="space-y-8">
              <div className="space-y-2">
                <div className="flex flex-wrap gap-2 mb-2">
                  <span className={cn(
                    "inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset uppercase tracking-wider",
                    job.site === 'saramin' ? "bg-blue-400/10 text-blue-400 ring-blue-400/20" : 
                    job.site === 'jobkorea' ? "bg-indigo-400/10 text-indigo-400 ring-indigo-400/20" :
                    "bg-emerald-400/10 text-emerald-400 ring-emerald-400/20"
                  )}>
                    {job.site}
                  </span>
                  {job.is_bookmarked && (
                    <span className="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium bg-primary/10 text-primary ring-1 ring-inset ring-primary/20 uppercase tracking-wider">
                      Bookmarked
                    </span>
                  )}
                  {job.ai_status === 'completed' && (
                    <span className={cn(
                      "inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset uppercase tracking-wider",
                      job.ai_score >= 80 ? "bg-green-500/10 text-green-500 ring-green-500/20" :
                      job.ai_score >= 50 ? "bg-yellow-500/10 text-yellow-500 ring-yellow-500/20" :
                      "bg-red-500/10 text-red-500 ring-red-500/20"
                    )}>
                      AI: {job.ai_score}% Match
                    </span>
                  )}
                </div>
                <h1 className="text-2xl sm:text-3xl font-bold text-foreground leading-tight">
                  {job.title}
                </h1>
                <div className="flex items-center gap-2 text-lg text-muted-foreground">
                  <Building2 className="h-5 w-5" />
                  <span className="font-medium">{job.company}</span>
                </div>
              </div>

              {/* AI Analysis Section */}
              <div className="rounded-xl border border-primary/20 bg-primary/5 p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-primary" />
                    <h3 className="font-bold text-sm uppercase tracking-wider">AI Analysis</h3>
                  </div>
                  {job.ai_status !== 'completed' && (
                    <Button 
                      size="sm" 
                      onClick={() => handleAnalyze()}
                      disabled={isAnalyzing || (!job.description && !job.description_image_url)}
                      className="h-8 gap-2 bg-primary/20 text-primary hover:bg-primary/30 border border-primary/30"
                    >
                      {isAnalyzing ? <Loader2 className="h-3 w-3 animate-spin" /> : <BrainCircuit className="h-3 w-3" />}
                      Run Analysis
                    </Button>
                  )}
                </div>

                {isAnalyzing ? (
                  <div className="py-4 flex flex-col items-center justify-center gap-2 text-primary/70">
                    <Loader2 className="h-6 w-6 animate-spin" />
                    <p className="text-xs font-mono animate-pulse uppercase">Evaluating suitability with GLM-4...</p>
                  </div>
                ) : job.ai_status === 'completed' ? (
                  <div className="space-y-4 animate-in fade-in slide-in-from-top-2">
                    <div className="flex items-end gap-3">
                      <div className="text-4xl font-black text-primary">{job.ai_score}%</div>
                      <div className="text-xs text-muted-foreground mb-1 uppercase font-mono tracking-tighter">Match Probability</div>
                    </div>
                    <div className="space-y-2">
                      {job.ai_summary?.split('\n').map((line, i) => (
                        <div key={i} className="flex gap-2 text-sm leading-relaxed text-foreground/80">
                          <CheckCircle2 className="h-4 w-4 text-primary mt-1 shrink-0" />
                          <span>{line.replace(/^[-\d.]\s*/, '')}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : job.ai_status === 'filtered' ? (
                  <div className="flex items-center gap-3 text-yellow-500/80 bg-yellow-500/5 p-3 rounded-lg border border-yellow-500/20">
                    <AlertCircle className="h-5 w-5 shrink-0" />
                    <p className="text-xs font-mono">{job.ai_summary || "FILTERED_BY_RULE_ENGINE"}</p>
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <p className="text-xs text-muted-foreground font-mono">
                      {(job.description || job.description_image_url) ? "Detailed analysis available via AI" : "No description data available for analysis"}
                    </p>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="flex items-start gap-3 p-4 rounded-lg bg-muted/30 border border-border/30">
                  <MapPin className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-xs font-mono uppercase text-muted-foreground mb-1">Location</p>
                    <p className="text-sm font-medium">{job.location || "Remote / Unspecified"}</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3 p-4 rounded-lg bg-muted/30 border border-border/30">
                  <DollarSign className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-xs font-mono uppercase text-muted-foreground mb-1">Salary</p>
                    <p className="text-sm font-medium">{job.salary || "Not Disclosed"}</p>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-4 rounded-lg bg-muted/30 border border-border/30">
                  <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-xs font-mono uppercase text-muted-foreground mb-1">Posted</p>
                    <p className="text-sm font-medium">{job.posted_at || job.created_at.split('T')[0]}</p>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-4 rounded-lg bg-muted/30 border border-border/30">
                  <Globe className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-xs font-mono uppercase text-muted-foreground mb-1">Source</p>
                    <a href={job.url} target="_blank" rel="noreferrer" className="text-sm font-medium hover:text-primary underline decoration-dotted underline-offset-4">
                      {new URL(job.url).hostname}
                    </a>
                  </div>
                </div>
              </div>
            </div>
          ) : null}
        </div>

        {job && (
          <div className="flex items-center justify-between border-t border-border/50 px-6 py-4 bg-muted/20">
            <Button
              variant="outline"
              onClick={() => handleToggleBookmark(job.id)}
              className={cn(
                "gap-2 border-input/50 hover:bg-background/50 transition-all",
                job.is_bookmarked && "border-primary/50 text-primary bg-primary/5 hover:bg-primary/10"
              )}
            >
              <Bookmark className={cn("h-4 w-4", job.is_bookmarked && "fill-current")} />
              {job.is_bookmarked ? "Bookmarked" : "Bookmark"}
            </Button>
            
            <Button 
              className="gap-2 bg-primary text-primary-foreground hover:bg-primary/90 shadow-lg shadow-primary/20"
              onClick={() => window.open(job.url, '_blank')}
            >
              View Original <ExternalLink className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>
    </div>,
    document.body
  );
}
