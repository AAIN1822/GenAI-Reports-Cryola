export interface SSOLoginResponse {
  status: string;
  message: string;
  data: SSOLogin;
}

export interface SSOLogin {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}
