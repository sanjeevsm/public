import React, { createContext, useContext, useState } from 'react';

export interface Currency {
  code: string;
  symbol: string;
  label: string;
  locale: string;
}

export const CURRENCIES: Currency[] = [
  { code: 'USD', symbol: '$',  label: 'US Dollar',           locale: 'en-US' },
  { code: 'EUR', symbol: '€',  label: 'Euro',                locale: 'de-DE' },
  { code: 'GBP', symbol: '£',  label: 'British Pound',       locale: 'en-GB' },
  { code: 'INR', symbol: '₹',  label: 'Indian Rupee',        locale: 'en-IN' },
  { code: 'JPY', symbol: '¥',  label: 'Japanese Yen',        locale: 'ja-JP' },
  { code: 'AUD', symbol: 'A$', label: 'Australian Dollar',   locale: 'en-AU' },
  { code: 'CAD', symbol: 'C$', label: 'Canadian Dollar',     locale: 'en-CA' },
  { code: 'SGD', symbol: 'S$', label: 'Singapore Dollar',    locale: 'en-SG' },
  { code: 'CHF', symbol: 'Fr', label: 'Swiss Franc',         locale: 'de-CH' },
  { code: 'CNY', symbol: '¥',  label: 'Chinese Yuan',        locale: 'zh-CN' },
  { code: 'HKD', symbol: 'HK$',label: 'Hong Kong Dollar',    locale: 'zh-HK' },
  { code: 'NZD', symbol: 'NZ$',label: 'New Zealand Dollar',  locale: 'en-NZ' },
  { code: 'SEK', symbol: 'kr', label: 'Swedish Krona',       locale: 'sv-SE' },
  { code: 'KRW', symbol: '₩',  label: 'South Korean Won',    locale: 'ko-KR' },
  { code: 'NOK', symbol: 'kr', label: 'Norwegian Krone',     locale: 'nb-NO' },
  { code: 'MXN', symbol: '$',  label: 'Mexican Peso',        locale: 'es-MX' },
  { code: 'BRL', symbol: 'R$', label: 'Brazilian Real',      locale: 'pt-BR' },
  { code: 'ZAR', symbol: 'R',  label: 'South African Rand',  locale: 'en-ZA' },
  { code: 'RUB', symbol: '₽',  label: 'Russian Ruble',       locale: 'ru-RU' },
  { code: 'AED', symbol: 'د.إ',label: 'UAE Dirham',          locale: 'ar-AE' },
  { code: 'THB', symbol: '฿',  label: 'Thai Baht',           locale: 'th-TH' },
  { code: 'MYR', symbol: 'RM', label: 'Malaysian Ringgit',   locale: 'ms-MY' },
  { code: 'IDR', symbol: 'Rp', label: 'Indonesian Rupiah',   locale: 'id-ID' },
  { code: 'PHP', symbol: '₱',  label: 'Philippine Peso',     locale: 'en-PH' },
  { code: 'PLN', symbol: 'zł', label: 'Polish Zloty',        locale: 'pl-PL' },
  { code: 'TRY', symbol: '₺',  label: 'Turkish Lira',        locale: 'tr-TR' },
];

export type DateFormat = 'MM/DD/YYYY' | 'DD/MM/YYYY' | 'YYYY-MM-DD';

interface SettingsContextValue {
  currency: string;
  setCurrency: (code: string) => void;
  selectedCurrencies: string[];  // Multi-currency support
  setSelectedCurrencies: (codes: string[]) => void;
  dateFormat: DateFormat;
  setDateFormat: (fmt: DateFormat) => void;
  transactionsPerPage: number;
  setTransactionsPerPage: (n: number) => void;
  formatCurrency: (amount: number, currencyCode?: string, compact?: boolean) => string;
  currencies: Currency[];
  getCurrency: (code: string) => Currency | undefined;
}

const SettingsContext = createContext<SettingsContextValue | null>(null);

export const SettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currency, setCurrencyState] = useState(
    () => localStorage.getItem('s_currency') ?? 'USD'
  );
  const [selectedCurrencies, setSelectedCurrenciesState] = useState<string[]>(
    () => {
      const saved = localStorage.getItem('s_selected_currencies');
      return saved ? JSON.parse(saved) : ['USD'];
    }
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
  const setSelectedCurrencies = (codes: string[]) => {
    localStorage.setItem('s_selected_currencies', JSON.stringify(codes));
    setSelectedCurrenciesState(codes);
    // Make sure primary currency is included
    if (codes.length > 0 && !codes.includes(currency)) {
      setCurrency(codes[0]);
    }
  };
  const setDateFormat = (fmt: DateFormat) => {
    localStorage.setItem('s_date_fmt', fmt);
    setDateFormatState(fmt);
  };
  const setTransactionsPerPage = (n: number) => {
    localStorage.setItem('s_tx_per_page', String(n));
    setTxPerPage(n);
  };

  const formatCurrency = (amount: number, currencyCode?: string, compact = false) => {
    const code = currencyCode || currency;
    const cur = CURRENCIES.find(c => c.code === code) ?? CURRENCIES[0];
    const opts: Intl.NumberFormatOptions = {
      style: 'currency',
      currency: cur.code,
      maximumFractionDigits: ['JPY', 'KRW', 'IDR'].includes(cur.code) ? 0 : 2,
      ...(compact && { notation: 'compact', maximumFractionDigits: 1 }),
    };
    return new Intl.NumberFormat(cur.locale, opts).format(amount);
  };

  const getCurrency = (code: string) => {
    return CURRENCIES.find(c => c.code === code);
  };

  return (
    <SettingsContext.Provider value={{
      currency, setCurrency,
      selectedCurrencies, setSelectedCurrencies,
      dateFormat, setDateFormat,
      transactionsPerPage, setTransactionsPerPage,
      formatCurrency,
      getCurrency,
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
