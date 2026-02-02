export type JobSite = "saramin" | "jobkorea" | "wanted";

export interface Job {
  id: number;
  title: string;
  company: string;
  url: string;
  site: JobSite;
  location: string | null;
  salary: string | null;
  experience: string | null;
  deadline: string | null;
  posted_at: string | null;
  is_bookmarked: boolean;
  created_at: string;
}

export interface Keyword {
  id: number;
  keyword: string;
  is_active: boolean;
  created_at: string;
}

export interface NewJobsCountResponse {
  count: number;
}

export interface JobStatsResponse {
  [site: string]: number;
}
