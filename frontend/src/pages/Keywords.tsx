import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getKeywords, createKeyword, deleteKeyword, crawlAll } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Trash2, Terminal, Activity, Loader2, AlertCircle, Search, Play, Zap } from "lucide-react";
import type { Keyword } from "@/types";

export default function Keywords() {
  const [newKeyword, setNewKeyword] = useState("");
  const queryClient = useQueryClient();

  const { data: keywords, isLoading, isError } = useQuery({
    queryKey: ["keywords"],
    queryFn: getKeywords,
  });

  const createMutation = useMutation({
    mutationFn: createKeyword,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["keywords"] });
      setNewKeyword("");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteKeyword,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["keywords"] });
    },
  });

  const crawlMutation = useMutation({
    mutationFn: crawlAll,
    onSuccess: () => {
      alert("Manual crawl started in the background for all keywords.");
    },
  });

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (newKeyword.trim()) {
      createMutation.mutate(newKeyword.trim());
    }
  };

  return (
    <div className="space-y-8 min-h-[calc(100vh-4rem)] p-1">
      <div className="flex flex-col gap-4 border-b border-zinc-800 pb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-zinc-900 rounded border border-zinc-800">
              <Terminal className="h-6 w-6 text-green-500" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight font-mono text-zinc-100">
                KEYWORD_DATABASE
              </h1>
              <p className="text-sm font-mono text-zinc-500 uppercase tracking-wider">
                Target configuration & Monitoring
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button
              onClick={() => crawlMutation.mutate()}
              disabled={crawlMutation.isPending || keywords?.length === 0}
              className="hidden md:flex items-center gap-2 px-4 py-2 rounded bg-green-500/10 border border-green-500/30 text-green-500 hover:bg-green-500/20 font-mono text-xs uppercase transition-all"
            >
              {crawlMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-3 w-3 fill-current" />}
              Execute Crawl Now
            </Button>
            <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded bg-zinc-900/50 border border-zinc-800">
              <Activity className="h-4 w-4 text-green-500" />
              <span className="text-xs font-mono text-green-500">SYSTEM_ONLINE</span>
            </div>
          </div>
        </div>

        <form onSubmit={handleAdd} className="relative mt-4 group">
          <div className="absolute inset-0 bg-green-500/5 blur-xl rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
          <div className="relative flex items-center gap-0 bg-black/40 border border-zinc-800 rounded-lg overflow-hidden focus-within:border-green-500/50 focus-within:ring-1 focus-within:ring-green-500/20 transition-all">
            <div className="pl-4 pr-2 text-zinc-600">
              <Search className="h-4 w-4" />
            </div>
            <input
              className="flex-1 bg-transparent border-none outline-none text-zinc-100 font-mono placeholder:text-zinc-700 h-12 text-sm"
              placeholder="ENTER_NEW_TARGET_KEYWORD..."
              value={newKeyword}
              onChange={(e) => setNewKeyword(e.target.value)}
              disabled={createMutation.isPending}
            />
            <Button
              type="submit"
              disabled={!newKeyword.trim() || createMutation.isPending}
              className="h-12 rounded-none px-6 bg-zinc-900 hover:bg-green-950 text-zinc-400 hover:text-green-500 border-l border-zinc-800 font-mono text-xs uppercase tracking-widest transition-all"
            >
              {createMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                "Add Keyword"
              )}
            </Button>
          </div>
        </form>
        
        {/* Mobile Crawl Button */}
        <Button
          onClick={() => crawlMutation.mutate()}
          disabled={crawlMutation.isPending || keywords?.length === 0}
          className="md:hidden w-full mt-2 flex items-center justify-center gap-2 bg-green-500/10 border border-green-500/30 text-green-500 font-mono text-xs uppercase"
        >
          {crawlMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-3 w-3 fill-current" />}
          Execute Crawl Now
        </Button>
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center h-64 gap-4 text-zinc-600">
          <Loader2 className="h-8 w-8 animate-spin text-green-500/50" />
          <span className="font-mono text-sm animate-pulse">FETCHING_DATA_STREAMS...</span>
        </div>
      ) : isError ? (
        <div className="flex items-center gap-4 p-4 border border-red-900/50 bg-red-950/10 rounded-lg text-red-500">
          <AlertCircle className="h-5 w-5" />
          <span className="font-mono">ERROR: CONNECTION_REFUSED</span>
        </div>
      ) : keywords?.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-64 border border-dashed border-zinc-800 rounded-lg bg-zinc-900/20">
          <Terminal className="h-12 w-12 text-zinc-700 mb-4" />
          <p className="text-zinc-500 font-mono">NO_TARGETS_DEFINED</p>
          <p className="text-zinc-700 text-xs font-mono mt-2">Input new keyword to begin monitoring</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {keywords?.map((k: Keyword) => (
            <div
              key={k.id}
              className="group relative overflow-hidden bg-zinc-950 border border-zinc-800 hover:border-green-500/30 transition-all duration-300 rounded-lg"
            >
              <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-green-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              
              <div className="p-5 flex flex-col gap-4">
                <div className="flex justify-between items-start">
                  <div className="space-y-1">
                    <h3 className="text-lg font-bold text-zinc-200 font-mono tracking-tight group-hover:text-green-400 transition-colors">
                      {k.keyword}
                    </h3>
                    <div className="flex items-center gap-2">
                      <span className={`h-1.5 w-1.5 rounded-full ${k.is_active ? "bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]" : "bg-red-500"}`} />
                      <span className={`text-[10px] font-mono tracking-wider ${k.is_active ? "text-green-500/70" : "text-red-500/70"}`}>
                        {k.is_active ? "ACTIVE_MONITORING" : "INACTIVE"}
                      </span>
                    </div>
                  </div>
                  
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-zinc-600 hover:text-red-500 hover:bg-red-500/10 transition-colors -mr-2 -mt-2 opacity-0 group-hover:opacity-100 focus:opacity-100"
                    onClick={() => deleteMutation.mutate(k.id)}
                    disabled={deleteMutation.isPending}
                  >
                    {deleteMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Trash2 className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                
                  <div className="flex items-center justify-between pt-4 border-t border-zinc-900">
                    <span className="text-[10px] font-mono text-zinc-700">ID: {String(k.id).padStart(4, '0')}</span>
                    <span className="text-[10px] font-mono text-zinc-700">
                      {k.created_at ? new Date(k.created_at).toLocaleDateString() : 'N/A'}
                    </span>
                  </div>
                </div>

            </div>
          ))}
        </div>
      )}
    </div>
  );
}