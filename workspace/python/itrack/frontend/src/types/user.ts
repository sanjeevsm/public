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
