import axiosInstance from "./axiosInstance";
import type { AxiosResponse } from "axios";
import type { LoginResponse } from "./model/LoginResponse";
import type { RegisterResponse } from "./model/RegisterResponse";
import type { SSOLoginResponse } from "./model/SSOLoginResponse";
import type { LogoutResponse } from "./model/LogoutResponse";

//Register User
export const registerUser = async (
  name: string,
  email: string,
  password: string,
  role_id: string
): Promise<AxiosResponse<RegisterResponse>> => {
  return axiosInstance.post("auth/register", {
    name,
    email,
    password,
    role_id,
  });
};

//  Login User
export const login = async (
  email: string,
  password: string
): Promise<AxiosResponse<LoginResponse>> => {
  return axiosInstance.post<LoginResponse>("auth/login", {
    email, 
    password,
  });
};

//  Forgot Password
export const forgotPassword = async (
  email: string
): Promise<AxiosResponse<any>> => {
  return axiosInstance.post("auth/forgot-password", { email });
};

//  Verify Otp
export const verifyOtp = async (
  email: string,
  otp: string
): Promise<AxiosResponse<any>> => {
  return axiosInstance.post("auth/validate-otp", { email, otp });
};

//  Resend Otp
export const resendOtp = async (
  email: string,
): Promise<AxiosResponse<any>> => {
  return axiosInstance.post("auth/resend-otp", { email });
};

// Reset Password
export const resetPassword = async (
  new_password: string,
  password_reset_token: string,
): Promise<AxiosResponse<any>> => {
  return axiosInstance.post("auth/reset-password", {
    new_password,
    password_reset_token
  });
};

export const ssoLogin = async (
  id_token: string,
  role_id: string
): Promise<AxiosResponse<SSOLoginResponse>> => {
  return axiosInstance.post("auth/sso/login", {
    id_token,
    role_id
  });
};

export const logout = async (): Promise<AxiosResponse<LogoutResponse>> => {
  return axiosInstance.get("auth/logout");
};
