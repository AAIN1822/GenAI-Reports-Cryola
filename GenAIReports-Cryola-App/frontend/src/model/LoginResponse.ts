export interface LoginResponse {
  token(arg0: string, token: any): unknown;
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  role_id: number;
  otp:number;
  new_password: number
}