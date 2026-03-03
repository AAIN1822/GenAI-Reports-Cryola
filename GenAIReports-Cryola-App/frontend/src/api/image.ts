import axiosInstance from "./axiosInstance";
import type { AxiosResponse } from "axios";
import type { ImageResponse } from "./model/ImageResponse";
 

export const getTemplateGallery = async (
  category: string,
  search: string,
  page: number
): Promise<AxiosResponse<ImageResponse>> => {
  return axiosInstance.get("image/template-gallery", {
    params: { category, search, page, page_size: 30 },
  });
};

export const getCrayolaGallery = async (
  search: string,
  page: number
): Promise<AxiosResponse<ImageResponse>> => {
  return axiosInstance.get("dam/image-listing", {
    params: { search, page, page_size: 30 },
  });
};

export const imageExistApi = async (
  category: string,
  image_name: string
): Promise<AxiosResponse<any>> => {
   const formData = new FormData();
    formData.append("category", category);
    formData.append("image_name", image_name);
  return axiosInstance.post("image/image-exist",formData, {
    headers: {
      "Content-Type": "multipart/form-data", // override here
    }})
}

type override_types = "overwrite" | "keep_both";

export const imageUploadCustom = async (
  category: string,
  image_name: string,
  action: override_types,
  file: File
): Promise<AxiosResponse<any>> => {
   const formData = new FormData();
    formData.append("category", category);
    formData.append("image_name", image_name);
    formData.append("action", action);
    formData.append("file", file)
  return axiosInstance.post("image/image-upload",formData, {
    headers: {
      "Content-Type": "multipart/form-data", // override here
    }})
}