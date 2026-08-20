import React from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Pie } from 'react-chartjs-2';
import { TransactionSummary } from '../types/transaction';
import { useSettings } from '../contexts/SettingsContext';

ChartJS.register(ArcElement, Tooltip, Legend);

const BG_COLORS = [
  'rgba(255, 99, 132, 0.8)',
  'rgba(54, 162, 235, 0.8)',
  'rgba(255, 206, 86, 0.8)',
  'rgba(75, 192, 192, 0.8)',
  'rgba(153, 102, 255, 0.8)',
  'rgba(255, 159, 64, 0.8)',
  'rgba(199, 199, 199, 0.8)',
  'rgba(83, 102, 255, 0.8)',
  'rgba(255, 99, 255, 0.8)',
  'rgba(99, 255, 132, 0.8)',
];
const BD_COLORS = BG_COLORS.map(c => c.replace('0.8', '1'));

interface Props {
  summary?: TransactionSummary;
  categoriesBreakdown?: Record<string, number>;
  title?: string;
}

export const CategoryChart: React.FC<Props> = ({ summary, categoriesBreakdown, title = 'Expenses by Category' }) => {
  const { formatCurrency } = useSettings();
  const breakdown = categoriesBreakdown ?? summary?.categories_breakdown ?? {};
  const categories = Object.keys(breakdown);
  const amounts = Object.values(breakdown);

  const chartData = {
    labels: categories,
    datasets: [{
      label: 'Amount',
      data: amounts,
      backgroundColor: BG_COLORS,
      borderColor: BD_COLORS,
      borderWidth: 1,
    }],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'right' as const },
      title: { display: true, text: title },
      tooltip: {
        callbacks: {
          label: (ctx: any) => ` ${ctx.label}: ${formatCurrency(ctx.parsed)}`,
        },
      },
    },
  };

  if (categories.length === 0) {
    return (
      <div>
        <h2 className="section-title">Category Breakdown</h2>
        <div className="empty-state" style={{ padding: '2rem' }}>No transactions yet</div>
      </div>
    );
  }

  return (
    <div>
      <h2 className="section-title">Category Breakdown</h2>
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <Pie data={chartData} options={options} />
      </div>
    </div>
  );
};
