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
  is_hidden: boolean;
  created_at: string;
  description?: string;
  description_image_url?: string;
  ai_status?: 'pending' | 'completed' | 'filtered' | 'failed';
  ai_score?: number;
  ai_summary?: string;
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

export interface TechSkill {
  name: string;
  level: string;
  description: string | null;
}

export interface UserProfile {
  tech_stack: TechSkill[];
  experience_years: number;
  interest_keywords: string[];
  exclude_keywords: string[];
  updated_at: string | null;
}
