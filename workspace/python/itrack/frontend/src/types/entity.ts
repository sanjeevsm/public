export type EntityType = 'Home' | 'Office' | 'Custom';
export type MemberRole = 'admin' | 'member';
export type TransactionMode = 'shared' | 'private';

export interface EntityMember {
  user_id: string;
  username: string;
  role: MemberRole;
  joined_at: string;
}

export interface Entity {
  id: string;
  name: string;
  entity_type: EntityType;
  custom_type_name?: string;
  description?: string;
  members: EntityMember[];
  created_by: string;
  created_at: string;
}

export interface EntityCreate {
  name: string;
  entity_type: EntityType;
  custom_type_name?: string;
  description?: string;
}

export interface EntityUpdate {
  name?: string;
  entity_type?: EntityType;
  custom_type_name?: string;
  description?: string;
}

export interface EntityInvite {
  user_email: string;
  role: MemberRole;
}

export interface MemberBreakdown {
  username: string;
  income: number;
  expense: number;
  balance: number;
}

export interface EntitySummary {
  entity_id: string;
  entity_name: string;
  total_balance: number;
  total_income: number;
  total_expense: number;
  shared_balance: number;
  shared_income: number;
  shared_expense: number;
  transaction_count: number;
  shared_transaction_count: number;
  categories_breakdown: Record<string, number>;
  member_breakdown: Record<string, MemberBreakdown>;
}
