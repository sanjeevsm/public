import React from 'react';
import { Settings, DollarSign, Calendar, List } from 'lucide-react';
import { useSettings, DateFormat } from '../contexts/SettingsContext';

const Section: React.FC<{ icon: React.ReactNode; title: string; description: string; children: React.ReactNode }> = ({
  icon, title, description, children,
}) => (
  <div className="card" style={{ padding: '1.5rem' }}>
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem', marginBottom: '1.25rem' }}>
      <div style={{
        width: 40, height: 40, borderRadius: 10,
        background: 'var(--primary-soft)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        color: 'var(--primary)', flexShrink: 0,
      }}>
        {icon}
      </div>
      <div>
        <h2 className="section-title" style={{ margin: 0 }}>{title}</h2>
        <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>{description}</p>
      </div>
    </div>
    {children}
  </div>
);

export const SettingsPage: React.FC = () => {
  const { 
    currency, setCurrency, 
    selectedCurrencies, setSelectedCurrencies,
    dateFormat, setDateFormat, 
    transactionsPerPage, setTransactionsPerPage,
    formatCurrency,
    formatDate,
    currencies
  } = useSettings();

  const toggleCurrency = (code: string) => {
    if (selectedCurrencies.includes(code)) {
      // Don't allow removing the last currency
      if (selectedCurrencies.length > 1) {
        setSelectedCurrencies(selectedCurrencies.filter(c => c !== code));
      }
    } else {
      setSelectedCurrencies([...selectedCurrencies, code]);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)', padding: '2rem 1.5rem' }}>
      <div style={{ maxWidth: 720, margin: '0 auto' }}>

        <div className="page-header" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem' }}>
          <Settings size={24} style={{ color: 'var(--primary)' }} />
          <div>
            <h1 className="page-title">Settings</h1>
            <p className="page-subtitle">Customize your iTrack+ experience</p>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

          {/* Currency Selection */}
          <Section
            icon={<DollarSign size={20} />}
            title="Active Currencies"
            description="Select one or more currencies to use in the app. Data will be tracked separately for each currency."
          >
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: '0.625rem' }}>
              {currencies.map(cur => {
                const isSelected = selectedCurrencies.includes(cur.code);
                const isPrimary = currency === cur.code;
                return (
                  <button
                    key={cur.code}
                    onClick={() => toggleCurrency(cur.code)}
                    style={{
                      padding: '0.75rem 1rem',
                      borderRadius: 10,
                      border: `2px solid ${isSelected ? 'var(--primary)' : 'var(--border)'}`,
                      background: isSelected ? 'var(--primary-soft)' : 'var(--surface-2)',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'all 0.15s',
                      position: 'relative',
                    }}
                  >
                    {isPrimary && (
                      <div style={{
                        position: 'absolute',
                        top: 4,
                        right: 4,
                        background: 'var(--primary)',
                        color: 'white',
                        fontSize: '0.6rem',
                        padding: '2px 6px',
                        borderRadius: 4,
                        fontWeight: 700,
                      }}>
                        PRIMARY
                      </div>
                    )}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                      <span style={{
                        fontSize: '1.125rem', fontWeight: 700,
                        color: isSelected ? 'var(--primary)' : 'var(--text)',
                      }}>
                        {cur.symbol}
                      </span>
                      <span style={{
                        fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.04em',
                        color: isSelected ? 'var(--primary)' : 'var(--text-secondary)',
                      }}>
                        {cur.code}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{cur.label}</div>
                  </button>
                );
              })}
            </div>
            <div style={{ marginTop: '1rem', padding: '0.75rem 1rem', background: 'var(--surface-2)', borderRadius: 8, fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
              <strong>Selected: </strong>{selectedCurrencies.length} {selectedCurrencies.length === 1 ? 'currency' : 'currencies'} 
              ({selectedCurrencies.map(c => currencies.find(cur => cur.code === c)?.code).join(', ')})
            </div>
          </Section>

          {/* Primary Currency */}
          <Section
            icon={<DollarSign size={20} />}
            title="Primary Currency"
            description="Choose your main currency for display. You can only select from active currencies."
          >
            <div style={{ display: 'flex', gap: '0.625rem', flexWrap: 'wrap' }}>
              {selectedCurrencies.map(code => {
                const cur = currencies.find(c => c.code === code);
                if (!cur) return null;
                return (
                  <button
                    key={cur.code}
                    onClick={() => setCurrency(cur.code)}
                    style={{
                      padding: '0.75rem 1rem',
                      borderRadius: 10,
                      border: `2px solid ${currency === cur.code ? 'var(--primary)' : 'var(--border)'}`,
                      background: currency === cur.code ? 'var(--primary-soft)' : 'var(--surface-2)',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'all 0.15s',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                    }}
                  >
                    <span style={{
                      fontSize: '1.125rem', fontWeight: 700,
                      color: currency === cur.code ? 'var(--primary)' : 'var(--text)',
                    }}>
                      {cur.symbol}
                    </span>
                    <span style={{
                      fontSize: '0.875rem', fontWeight: 600,
                      color: currency === cur.code ? 'var(--primary)' : 'var(--text-secondary)',
                    }}>
                      {cur.code}
                    </span>
                  </button>
                );
              })}
            </div>
            <div style={{ marginTop: '1rem', padding: '0.75rem 1rem', background: 'var(--surface-2)', borderRadius: 8, fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
              Preview: {formatCurrency(1234.56)} • {formatCurrency(-500)}
            </div>
          </Section>

          {/* Date Format */}
          <Section
            icon={<Calendar size={20} />}
            title="Date Format"
            description="Choose how dates are displayed throughout the application"
          >
            <div style={{ display: 'flex', gap: '0.625rem', flexWrap: 'wrap' }}>
              {(['MM/DD/YYYY', 'DD/MM/YYYY', 'YYYY-MM-DD', 'DD-MM-YYYY', 'DD-MMM-YYYY', 'MMM DD, YYYY'] as DateFormat[]).map(fmt => (
                <button
                  key={fmt}
                  onClick={() => setDateFormat(fmt)}
                  style={{
                    padding: '0.625rem 1.25rem',
                    borderRadius: 8,
                    border: `2px solid ${dateFormat === fmt ? 'var(--primary)' : 'var(--border)'}`,
                    background: dateFormat === fmt ? 'var(--primary-soft)' : 'var(--surface-2)',
                    color: dateFormat === fmt ? 'var(--primary)' : 'var(--text)',
                    fontWeight: dateFormat === fmt ? 600 : 400,
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    transition: 'all 0.15s',
                  }}
                >
                  {fmt}
                </button>
              ))}
            </div>
            <div style={{ marginTop: '1rem', padding: '0.75rem 1rem', background: 'var(--surface-2)', borderRadius: 8, fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
              Preview: {formatDate(new Date())}
            </div>
          </Section>

          {/* Transactions per page */}
          <Section
            icon={<List size={20} />}
            title="Transactions Per Page"
            description="Number of transactions shown per page in the transaction list"
          >
            <div style={{ display: 'flex', gap: '0.625rem' }}>
              {[25, 50, 100].map(n => (
                <button
                  key={n}
                  onClick={() => setTransactionsPerPage(n)}
                  style={{
                    padding: '0.625rem 1.5rem',
                    borderRadius: 8,
                    border: `2px solid ${transactionsPerPage === n ? 'var(--primary)' : 'var(--border)'}`,
                    background: transactionsPerPage === n ? 'var(--primary-soft)' : 'var(--surface-2)',
                    color: transactionsPerPage === n ? 'var(--primary)' : 'var(--text)',
                    fontWeight: transactionsPerPage === n ? 600 : 400,
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    transition: 'all 0.15s',
                  }}
                >
                  {n}
                </button>
              ))}
            </div>
          </Section>

        </div>
      </div>
    </div>
  );
};
