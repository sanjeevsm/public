export type BudgetPeriod = 'daily' | 'weekly' | 'monthly' | 'yearly';
export type BudgetType = 'category' | 'total';

export interface Budget {
  id: string;
  name: string;
  amount: number;
  period: BudgetPeriod;
  budget_type: BudgetType;
  category?: string;
  start_date: string;
  end_date?: string;
  alert_threshold: number;
  user_id: string;
  entity_id?: string;
  created_at: string;
}

export interface BudgetCreate {
  name: string;
  amount: number;
  period: BudgetPeriod;
  budget_type: BudgetType;
  category?: string;
  start_date: string;
  end_date?: string;
  alert_threshold?: number;
}

export interface BudgetUpdate {
  name?: string;
  amount?: number;
  period?: BudgetPeriod;
  budget_type?: BudgetType;
  category?: string;
  start_date?: string;
  end_date?: string;
  alert_threshold?: number;
}

export interface BudgetProgress {
  budget_id: string;
  budget_name: string;
  budget_amount: number;
  spent_amount: number;
  remaining_amount: number;
  percentage_spent: number;
  is_exceeded: boolean;
  is_alert: boolean;
  period: BudgetPeriod;
  category?: string;
  days_remaining?: number;
}
