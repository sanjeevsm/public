export type CategoryType = 'income' | 'expense' | 'asset' | 'liability' | 'both';

export interface Category {
  id: string;
  name: string;
  type: CategoryType;
  color?: string;
  icon?: string;
  description?: string;
  is_default: boolean;
  user_id?: string;
  entity_id?: string;
  created_at: string;
}

export interface CategoryCreate {
  name: string;
  type: CategoryType;
  color?: string;
  icon?: string;
  description?: string;
  is_default?: boolean;
}

export interface CategoryUpdate {
  name?: string;
  type?: CategoryType;
  color?: string;
  icon?: string;
  description?: string;
}

export interface CategoryStats {
  [categoryName: string]: {
    count: number;
    total_amount: number;
  };
}
