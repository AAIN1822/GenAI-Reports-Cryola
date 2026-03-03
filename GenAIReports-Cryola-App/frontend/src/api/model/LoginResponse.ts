
export interface LoginResponse {
  status: string;
  message: string;
  data: LoginData;
}

export interface LoginData {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number; // in seconds
}