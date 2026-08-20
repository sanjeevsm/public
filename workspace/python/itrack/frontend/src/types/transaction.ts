export type TransactionType = 'income' | 'expense' | 'asset' | 'liability';
export type TransactionMode = 'shared' | 'private';

export interface Transaction {
  id: string;
  description: string;
  amount: number;
  type: TransactionType;
  category: string;
  date: string;
  mode?: TransactionMode;
  currency: string;
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
  currency?: string;
  is_recurring?: boolean;
  recurrence?: 'monthly' | undefined;
  recurrence_start?: string | undefined;
}

export interface TransactionSummary {
  total_balance: number;
  total_income: number;
  total_expense: number;
  total_assets: number;
  total_liabilities: number;
  net_worth: number;
  income_count: number;
  expense_count: number;
  asset_count: number;
  liability_count: number;
  categories_breakdown: Record<string, number>;
  currency: string;
}

export interface ImportResult {
  imported: number;
  failed: number;
  errors: string[];
}

export interface MonthlyDataPoint {
  year: number;
  month: number;
  income: number;
  expense: number;
  balance: number;
}

export interface RecurringTransaction {
  id: string;
  type: 'income' | 'expense';
  amount: number;
  description: string;
  recurrence_start: string | null;
}
