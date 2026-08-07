import React from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Pie } from 'react-chartjs-2';
import { TransactionSummary } from '../types/transaction';

ChartJS.register(ArcElement, Tooltip, Legend);

interface Props {
  summary: TransactionSummary;
}

export const CategoryChart: React.FC<Props> = ({ summary }) => {
  const categories = Object.keys(summary.categories_breakdown);
  const amounts = Object.values(summary.categories_breakdown);

  const data = {
    labels: categories,
    datasets: [
      {
        label: 'Amount ($)',
        data: amounts,
        backgroundColor: [
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
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)',
          'rgba(199, 199, 199, 1)',
          'rgba(83, 102, 255, 1)',
          'rgba(255, 99, 255, 1)',
          'rgba(99, 255, 132, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right' as const,
      },
      title: {
        display: true,
        text: 'Expenses by Category',
      },
    },
  };

  if (categories.length === 0) {
    return (
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Category Breakdown</h2>
        <p className="text-gray-500 text-center py-8">No transactions yet</p>
      </div>
    );
  }

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Category Breakdown</h2>
      <div className="flex justify-center">
        <Pie data={data} options={options} />
      </div>
    </div>
  );
};
