import axiosInstance from "./axiosInstance";
import type { AxiosResponse } from "axios";

interface DeleteResponse {
  [x: string]: any;
    status: string;
    message: string;
     data: string;
}

export const deleteFromBlob = async (
  blob_url: string
): Promise<AxiosResponse<DeleteResponse>> => {
  return axiosInstance.delete(`image/delete-image?url=${blob_url}`,{
  });
};

export const refinementUpload = async(project_id: string, stage: string, image_name: string, file: File): Promise<AxiosResponse<any>> => {
  const formData = new FormData();
  formData.append("project_id", project_id);
  formData.append("stage", stage);
  formData.append("image_name", image_name);
  formData.append("file", file);
  return axiosInstance.post(`image/refinement-upload`,
    formData, {
      headers: { "Content-Type": "multipart/form-data" }
    }
  )
}

export const refinementDelete = async (
  project_id: string,
  url: string
): Promise<AxiosResponse<DeleteResponse>> => {
  return axiosInstance.delete(`image/refinement-delete?project_id=${project_id}&url=${url}`,{
  });
};