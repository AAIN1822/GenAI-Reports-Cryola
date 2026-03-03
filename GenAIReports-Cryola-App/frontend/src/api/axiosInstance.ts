import axios, {
  AxiosError,
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from "axios";
import { logoutUser } from "../utils/helpers";

const apiUrl = import.meta.env.VITE_API_URL;

let refreshPromise: Promise<string> | null = null;

const axiosInstance: AxiosInstance = axios.create({
  baseURL: apiUrl,
  headers: { "Content-Type": "application/json" },
});

// -----------------------------------------------------
// Helper: Refresh Token Function (single call only)
// -----------------------------------------------------
const refreshAccessToken = async (): Promise<string> => {
  if (!refreshPromise) {
    const refresh_token = localStorage.getItem("refresh_token");

    refreshPromise = axios
      .post(`${apiUrl}/auth/refresh`, { refresh_token })
      .then((res) => {
        const newAccess = res.data.data.access_token;
        localStorage.setItem("access_token", newAccess);
        return newAccess;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }

  return refreshPromise;
};

// -----------------------------------------------------
// REQUEST: attach access token
// -----------------------------------------------------
axiosInstance.interceptors.request.use(
  (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
    const token = localStorage.getItem("access_token");

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// -----------------------------------------------------
// RESPONSE: auto refresh token and retry
// -----------------------------------------------------

let hasShownSessionExpiredAlert = false;

axiosInstance.interceptors.response.use(
  (response: AxiosResponse) => response,

  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & {
      _retry?: boolean;
    };

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const newToken = await refreshAccessToken();

        originalRequest.headers = {
          ...originalRequest.headers,
          Authorization: `Bearer ${newToken}`,
        };

        return axiosInstance(originalRequest);
      } catch (err) {
        if (!hasShownSessionExpiredAlert) {
          hasShownSessionExpiredAlert = true;
          alert("Your session has expired, please login again.");
        }
        logoutUser();
        window.location.href = "/";
      }
    }

    return Promise.reject(error);
  }
);

export default axiosInstance;
