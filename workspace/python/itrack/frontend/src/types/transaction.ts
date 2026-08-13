export type TransactionType = 'income' | 'expense';
export type TransactionMode = 'shared' | 'private';

export interface Transaction {
  id: string;
  description: string;
  amount: number;
  type: TransactionType;
  category: string;
  date: string;
  mode?: TransactionMode;
  entity_id?: string;
  username?: string;
  created_at: string;
}

export interface TransactionInput {
  description: string;
  amount: number;
  type: TransactionType;
  category: string;
  date: string;
  mode?: TransactionMode;
  is_recurring?: boolean;
  recurrence?: 'monthly' | undefined;
  recurrence_start?: string | undefined;
}

export interface TransactionSummary {
  total_balance: number;
  total_income: number;
  total_expense: number;
  income_count: number;
  expense_count: number;
  categories_breakdown: Record<string, number>;
}

export interface ImportResult {
  imported: number;
  failed: number;
  errors: string[];
}
