import axiosInstance from "./axiosInstance";
import type { AxiosResponse } from "axios";
import type { MeResponse } from "./model/MeResponse";
import type { ChangePasswordResponse } from "./model/ChangePasswordResponse";

export const getMe = async (): Promise<AxiosResponse<MeResponse>> => {
  return axiosInstance.get("user/me");
};

export const changePassword = async (
  old_password: string,
  new_password: string
): Promise<AxiosResponse<ChangePasswordResponse>> => {
  return axiosInstance.post("user/change-password", {
    old_password,
    new_password,
  });
};
