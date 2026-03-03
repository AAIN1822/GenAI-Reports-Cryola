import axiosInstance from "./axiosInstance";
import type { AxiosResponse } from "axios";
import type { AIResponse, AIJobStatusResponse } from "./model/aiResponse";

export const applyAIColorTheme = async (
  project_id: string
): Promise<AxiosResponse<AIResponse>> => {
  return axiosInstance.get(`ai/colour_theme/${project_id}`);
};

export const applyAIColorThemeRegeneration = async (
  project_id: string,
  choosen_url: string,
  feedback_prompt: string
): Promise<AxiosResponse<AIResponse>> => {
  return axiosInstance.post(`ai/colour_theme_refinement/${project_id}`, {
    choosen_url,
    feedback_prompt,
  });
};

export const feedback = async (
  project_id: string,
  image_url: string,
  like: boolean,
  stage: string
): Promise<AxiosResponse<any>> => {
  return axiosInstance.post(`ai/feedback/${project_id}`, {
    image_url,
    like,
    stage,
  });
};

export const applyAIGraphics = async (
  project_id: string,
  choosen_url: string,
  score: number
): Promise<AxiosResponse<AIResponse>> => {
  return axiosInstance.post(`ai/graphics/${project_id}`, {
    choosen_url,
    score,
  });
};

export const applyAIGraphicsRegeneration = async (
  project_id: string,
  selected_graphics_url: string,
  feedback_prompt: string
): Promise<AxiosResponse<AIResponse>> => {
  return axiosInstance.post(`ai/graphics_refinement/${project_id}`, {
    selected_graphics_url,
    feedback_prompt,
  });
};

export const applyAIPlacement = async (
  project_id: string,
  choosen_url: string,
  score: number
): Promise<AxiosResponse<AIResponse>> => {
  return axiosInstance.post(`ai/product_placement/${project_id}`, {
    choosen_url,
    score,
  });
};

export const applyAIPlacementRegeneration = async (
  project_id: string,
  choosen_url: string,
  feedback_prompt: string
): Promise<AxiosResponse<AIResponse>> => {
  return axiosInstance.post(`ai/product_placement_refinement/${project_id}`, {
    choosen_url,
    feedback_prompt,
  });
};

export const getJobStatus = async (
  job_id: string
): Promise<AxiosResponse<AIJobStatusResponse>> => {
  return axiosInstance.get(`ai/status/${job_id}`);
};

export const fetchMultiAngleView = async (
  project_id: string,
  choosen_url: string,
  score: number
): Promise<AxiosResponse<any>> => {
  return axiosInstance.post(`ai/multi_angle_view/${project_id}`,{
    choosen_url,
    score,
  });
};