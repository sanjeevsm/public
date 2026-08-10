export interface User {
  id: string;
  username: string;
  email: string;
  entity_id?: string;
  entity_role?: string;
  created_at: string;
}

export interface UserRegister {
  username: string;
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface UserUpdate {
  username?: string;
  email?: string;
  current_password?: string;
  new_password?: string;
}

export interface AdminUserUpdate {
  username?: string;
  email?: string;
}
