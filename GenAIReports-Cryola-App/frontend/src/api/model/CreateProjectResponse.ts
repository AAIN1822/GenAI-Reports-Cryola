export interface CreateProjectResponse {
  status: string;
  message: string;
  data: CreateProject;
}

export interface CreateProject {
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
