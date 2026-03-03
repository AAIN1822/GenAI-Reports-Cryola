export interface MeResponse {
  status: string;
  message: string;
  data: User;
}

export interface User {
  id: string;
  name: string;
  email: string;
  role_id: string;
  login_type: string;
  last_login_time: number;
}
