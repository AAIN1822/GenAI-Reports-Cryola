import axiosInstance from "./axiosInstance";
import type { AxiosResponse } from "axios";
import type { CreateProjectResponse } from "./model/CreateProjectResponse";
import type { ProjectHistoryResponse } from "./model/ProjectHistroyResponse";

export const createNewProject = async (
  account: string,
  structure: string,
  sub_brand: string,
  season: string,
  region: string,
  project_description: string
): Promise<AxiosResponse<CreateProjectResponse>> => {
  return axiosInstance.post("projects/new-project", {
    account,
    structure,
    sub_brand,
    season,
    region,
    project_description,
  });
};

export const projectHistory = async (
  search: string,
  account: string,
  structure: string,
  sub_brand: string,
  season: string,
  region: string,
  page: number,
  page_size: number,
  sort_by: string,
  sort_order: string
): Promise<AxiosResponse<ProjectHistoryResponse>> => {
  return axiosInstance.get("projects/history",{
    params: {
    search,
    account,
    structure,
    sub_brand,
    season,
    region,
    page,
    page_size,
    sort_by,
    sort_order 
  }
  });
};

export const updateProject = async (
  project_id: string,
  project_details: Record<string, any>
): Promise<AxiosResponse<any>> => {
  return axiosInstance.put(`projects/${project_id}/update`, project_details);
};

export const fetchProject = async(project_id: string): Promise<AxiosResponse<any>> => {
  return axiosInstance.get(`projects/${project_id}`)
}

export const saveAsProject = async (
  project_id: string,
  account: string,
  structure: string,
  sub_brand: string,
  season: string,
  region: string,
  project_description: string
): Promise<AxiosResponse<any>> => {
  return axiosInstance.post(`projects/save_as/${project_id}`, {
    account,
    structure,
    sub_brand,
    season,
    region,
    project_description,
  });
};

export const downloadProjectAssets = async (
  project_id: string
): Promise<AxiosResponse<any>> => {  
  return axiosInstance.get(`projects/download_project/${project_id}`, {
    responseType: "blob", // 🔑 REQUIRED
  });
};