import React, { createContext, useContext, useState } from 'react';

export interface Currency {
  code: string;
  symbol: string;
  label: string;
  locale: string;
}

export const CURRENCIES: Currency[] = [
  { code: 'USD', symbol: '$',  label: 'US Dollar',         locale: 'en-US' },
  { code: 'EUR', symbol: '€',  label: 'Euro',              locale: 'de-DE' },
  { code: 'GBP', symbol: '£',  label: 'British Pound',     locale: 'en-GB' },
  { code: 'INR', symbol: '₹',  label: 'Indian Rupee',      locale: 'en-IN' },
  { code: 'JPY', symbol: '¥',  label: 'Japanese Yen',      locale: 'ja-JP' },
  { code: 'AUD', symbol: 'A$', label: 'Australian Dollar', locale: 'en-AU' },
  { code: 'CAD', symbol: 'C$', label: 'Canadian Dollar',   locale: 'en-CA' },
  { code: 'SGD', symbol: 'S$', label: 'Singapore Dollar',  locale: 'en-SG' },
];

export type DateFormat = 'MM/DD/YYYY' | 'DD/MM/YYYY' | 'YYYY-MM-DD';

interface SettingsContextValue {
  currency: string;
  setCurrency: (code: string) => void;
  dateFormat: DateFormat;
  setDateFormat: (fmt: DateFormat) => void;
  transactionsPerPage: number;
  setTransactionsPerPage: (n: number) => void;
  formatCurrency: (amount: number, compact?: boolean) => string;
  currencies: Currency[];
}

const SettingsContext = createContext<SettingsContextValue | null>(null);

export const SettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currency, setCurrencyState] = useState(
    () => localStorage.getItem('s_currency') ?? 'USD'
  );
  const [dateFormat, setDateFormatState] = useState<DateFormat>(
    () => (localStorage.getItem('s_date_fmt') as DateFormat) ?? 'MM/DD/YYYY'
  );
  const [transactionsPerPage, setTxPerPage] = useState(
    () => Number(localStorage.getItem('s_tx_per_page') ?? '50')
  );

  const setCurrency = (code: string) => {
    localStorage.setItem('s_currency', code);
    setCurrencyState(code);
  };
  const setDateFormat = (fmt: DateFormat) => {
    localStorage.setItem('s_date_fmt', fmt);
    setDateFormatState(fmt);
  };
  const setTransactionsPerPage = (n: number) => {
    localStorage.setItem('s_tx_per_page', String(n));
    setTxPerPage(n);
  };

  const formatCurrency = (amount: number, compact = false) => {
    const cur = CURRENCIES.find(c => c.code === currency) ?? CURRENCIES[0];
    const opts: Intl.NumberFormatOptions = {
      style: 'currency',
      currency: cur.code,
      maximumFractionDigits: cur.code === 'JPY' ? 0 : 2,
      ...(compact && { notation: 'compact', maximumFractionDigits: 1 }),
    };
    return new Intl.NumberFormat(cur.locale, opts).format(amount);
  };

  return (
    <SettingsContext.Provider value={{
      currency, setCurrency,
      dateFormat, setDateFormat,
      transactionsPerPage, setTransactionsPerPage,
      formatCurrency,
      currencies: CURRENCIES,
    }}>
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = (): SettingsContextValue => {
  const ctx = useContext(SettingsContext);
  if (!ctx) throw new Error('useSettings must be inside SettingsProvider');
  return ctx;
};
