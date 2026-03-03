import axiosInstance from "./axiosInstance";
import type { AxiosResponse } from "axios";
import type { MasterDataResponse } from "./model/MasterDataResponse";
import type { MasterAddResponse } from "./model/MasterAddResponse";
import type { MasterDeleteResponse } from "./model/MasterDeleteResponse";

export const getAccounts = async (): Promise<AxiosResponse<MasterDataResponse>> => {
  return axiosInstance.get("master/md_accounts");
};

export const addAccounts = async (
  name: string
): Promise<AxiosResponse<MasterAddResponse>> => {
  return axiosInstance.post("master/md_accounts", {name});
};

export const deleteAccounts = async (
  id: string
): Promise<AxiosResponse<MasterDeleteResponse>> => {
  return axiosInstance.delete(`master/md_accounts/${id}`);
};

export const getSeasons = async (): Promise<AxiosResponse<MasterDataResponse>> => {
  return axiosInstance.get("master/md_seasons");
};

export const addSeasons = async (
  name: string
): Promise<AxiosResponse<MasterAddResponse>> => {
  return axiosInstance.post("master/md_seasons", {name});
};

export const deleteSeasons = async (
  id: string
): Promise<AxiosResponse<MasterDeleteResponse>> => {
  return axiosInstance.delete(`master/md_seasons/${id}`);
};

export const getSubBrands = async (): Promise<AxiosResponse<MasterDataResponse>> => {
  return axiosInstance.get("master/md_subbrands");
};

export const addSubBrands = async (
  name: string
): Promise<AxiosResponse<MasterAddResponse>> => {
  return axiosInstance.post("master/md_subbrands", {name});
};

export const deleteSubBrands = async (
  id: string
): Promise<AxiosResponse<MasterDeleteResponse>> => {
  return axiosInstance.delete(`master/md_subbrands/${id}`);
};

export const getStructures = async (): Promise<AxiosResponse<MasterDataResponse>> => {
  return axiosInstance.get("master/md_structures");
};

export const addStructures = async (
  name: string
): Promise<AxiosResponse<MasterAddResponse>> => {
  return axiosInstance.post("master/md_structures", {name});
};

export const deleteStructures = async (
  id: string
): Promise<AxiosResponse<MasterDeleteResponse>> => {
  return axiosInstance.delete(`master/md_structures/${id}`);
};

export const getRegions = async (): Promise<AxiosResponse<MasterDataResponse>> => {
  return axiosInstance.get("master/md_regions");
};

export const addRegions = async (
  name: string
): Promise<AxiosResponse<MasterAddResponse>> => {
  return axiosInstance.post("master/md_regions", {name});
};

export const deleteRegions = async (
  id: string
): Promise<AxiosResponse<MasterDeleteResponse>> => {
  return axiosInstance.delete(`master/md_regions/${id}`);
};

export const getDisplayDimension =  async(): Promise<AxiosResponse<any>> => {
  return axiosInstance.get("master/md_display_dimensions")
}

export const addDisplayDimension =  async(
  name: string,
): Promise<AxiosResponse<any>> => {
  return axiosInstance.post("master/md_display_dimensions", {name})
}

export const deleteDisplayDimension =  async(
  id: string
): Promise<AxiosResponse<any>> => {
  return axiosInstance.delete(`master/md_display_dimensions/${id}`)
}

export const getProductDimension =  async(): Promise<AxiosResponse<any>> => {
  return axiosInstance.get("master/md_product_dimensions")
}

export const addProductDimension =  async(
  name: string,
): Promise<AxiosResponse<any>> => {
  return axiosInstance.post("master/md_product_dimensions", {name})
}

export const deleteProductDimension =  async(
  id: string
): Promise<AxiosResponse<any>> => {
  return axiosInstance.delete(`master/md_product_dimensions/${id}`)
}