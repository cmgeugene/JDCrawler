import { useJobStats } from "@/queries/useJobStats";
import { useNewJobsCount } from "@/queries/useNewJobsCount";
import { CrawlTrigger } from "@/components/CrawlTrigger";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading, error: statsError } = useJobStats();
  const { data: newJobs, isLoading: newJobsLoading } = useNewJobsCount();

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
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Overview of current crawling status and statistics.</p>
      </div>

      <CrawlTrigger />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Total Jobs", value: totalJobs.toLocaleString(), change: "Total collected" },
          { label: "New Jobs", value: newJobs?.count.toLocaleString() || "0", change: "Since last check" },
          { label: "Active Crawlers", value: "3", change: "Saramin, JobKorea, Wanted" },
          { label: "Service Status", value: "Operational", change: "All systems go" }
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
                tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                dy={10}
              />
              <YAxis
                tickLine={false}
                axisLine={false}
                tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
              />
              <Tooltip
                cursor={{ fill: 'hsl(var(--muted))' }}
                contentStyle={{
                  borderRadius: '0.5rem',
                  border: '1px solid hsl(var(--border))',
                  backgroundColor: 'hsl(var(--background))',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                }}
              />
              <Bar
                dataKey="value"
                fill="hsl(var(--primary))"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
