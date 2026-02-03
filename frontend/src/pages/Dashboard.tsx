import { useState, useEffect } from "react";
import { useJobStats } from "@/queries/useJobStats";
import { useNewJobsCount } from "@/queries/useNewJobsCount";
import { getCrawlStatus } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { Clock, Timer, Calendar as CalendarIcon, Activity } from "lucide-react";

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading, error: statsError } = useJobStats();
  const { data: newJobs, isLoading: newJobsLoading } = useNewJobsCount();
  const { data: crawlStatus } = useQuery({
    queryKey: ["crawlStatus"],
    queryFn: getCrawlStatus,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const [timeLeft, setTimeLeft] = useState<string>("");

  useEffect(() => {
    const nextRun = crawlStatus?.jobs?.[0]?.next_run_time;
    if (!nextRun) {
      setTimeLeft("Not scheduled");
      return;
    }

    const timer = setInterval(() => {
      const now = new Date().getTime();
      const distance = new Date(nextRun).getTime() - now;

      if (distance < 0) {
        setTimeLeft("Running...");
      } else {
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        setTimeLeft(`${hours}h ${minutes}m ${seconds}s`);
      }
    }, 1000);

    return () => clearInterval(timer);
  }, [crawlStatus]);

  if (statsLoading || newJobsLoading) {
    return <div className="p-8 text-center text-muted-foreground animate-pulse">Loading dashboard...</div>;
  }

  if (statsError) {
    return <div className="p-8 text-center text-destructive">Failed to load dashboard data. Please check the backend connection.</div>;
  }

  const chartData = stats
    ? Object.entries(stats).map(([name, value]) => ({ name, value }))
    : [];

  const totalJobs = chartData.reduce((acc, curr) => acc + curr.value, 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight text-primary">Dashboard</h1>
        <p className="text-muted-foreground">Overview of current crawling status and statistics.</p>
      </div>

      {/* Schedule Status Section */}
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-xl border bg-card/50 p-6 flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-500/10 rounded-full">
              <Clock className="h-6 w-6 text-blue-500" />
            </div>
            <div>
              <p className="text-xs font-mono uppercase text-muted-foreground">Next Scheduled Run</p>
              <p className="text-lg font-bold font-mono">
                {crawlStatus?.jobs?.[0]?.next_run_time 
                  ? new Date(crawlStatus.jobs[0].next_run_time).toLocaleString() 
                  : "N/A"}
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center gap-2 text-blue-500 justify-end mb-1">
              <Timer className="h-4 w-4" />
              <span className="text-xs font-bold uppercase font-mono">Time Remaining</span>
            </div>
            <p className="text-2xl font-black font-mono tracking-tighter text-blue-500/80">{timeLeft}</p>
          </div>
        </div>

        <div className="rounded-xl border bg-card/50 p-6 flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-emerald-500/10 rounded-full">
              <Activity className="h-6 w-6 text-emerald-500" />
            </div>
            <div>
              <p className="text-xs font-mono uppercase text-muted-foreground">Scheduler Status</p>
              <p className="text-lg font-bold font-mono uppercase">
                {crawlStatus?.status === 'running' ? 'Active & Monitoring' : 'Idle'}
              </p>
            </div>
          </div>
          <div className="h-2 w-2 rounded-full bg-emerald-500 animate-ping" />
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Total Jobs", value: totalJobs.toLocaleString(), change: "Total collected", icon: CalendarIcon },
          { label: "New Jobs", value: newJobs?.count.toLocaleString() || "0", change: "Since last check", icon: Activity },
          { label: "Active Crawlers", value: "3", change: "Saramin, JobKorea, Wanted", icon: Timer },
          { label: "Service Status", value: "Operational", change: "All systems go", icon: Clock }
        ].map((stat, i) => (
          <div key={i} className="rounded-xl border bg-card p-6 shadow-sm transition-all hover:shadow-md">
            <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{stat.label}</div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-bold">{stat.value}</span>
              <span className="text-xs text-muted-foreground">{stat.change}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="rounded-xl border bg-card p-6 shadow-sm min-h-[300px]">
        <h3 className="text-lg font-medium mb-6">Jobs by Site</h3>
        <div className="h-[300px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis
                dataKey="name"
                tickLine={false}
                axisLine={false}
                tick={{ fill: 'var(--muted-foreground)', fontSize: 12 }}
                dy={10}
              />
              <YAxis
                tickLine={false}
                axisLine={false}
                tick={{ fill: 'var(--muted-foreground)', fontSize: 12 }}
              />
              <Tooltip
                cursor={{ fill: 'var(--muted)', opacity: 0.4 }}
                contentStyle={{
                  borderRadius: '0.5rem',
                  border: '1px solid var(--border)',
                  backgroundColor: 'var(--background)',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                }}
              />
              <Bar
                dataKey="value"
                fill="var(--chart-1)"
                radius={[4, 4, 0, 0]}
                barSize={48}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}