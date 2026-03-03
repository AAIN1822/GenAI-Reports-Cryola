export interface ProjectHistoryResponse {
  status: string;
  message: string;
  data: Data;
}

type Pagination = {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface Data {
  pagination: Pagination;
  projects: Project[];
}

export interface Project {
  id: string;
  account: string;
  structure: string;
  sub_brand: string;
  season: string;
  region: string;
  project_description: string;
  created_by: string;
  created_at: string;
}
