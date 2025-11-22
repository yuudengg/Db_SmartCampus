export interface LoginResponse {
  success: boolean;
  message?: string;
  user_id?: number;
  name?: string;
  role?: string;
}

export interface RegisterResponse {
  success: boolean;
  message: string;
}
