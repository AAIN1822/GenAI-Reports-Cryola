export interface RegisterResponse {
  status: string;
  message: string;
  data: Register;
}

export interface Register {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}
