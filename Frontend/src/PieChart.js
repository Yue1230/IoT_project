import React from "react";
import { Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend
);

const PieChart = ({ stats, totalTarget = 20 }) => {
  // 計算當前完成的總數
  const completed = Object.values(stats).reduce((a, b) => a + b, 0);
  const remaining = totalTarget - completed;

  const data = {
    labels: ['已完成', '未完成'],
    datasets: [
      {
        data: [completed, remaining],
        backgroundColor: [
          'rgba(75, 192, 192, 0.6)',  // 完成的部分
          'rgba(201, 203, 207, 0.6)'   // 未完成的部分
        ],
        borderColor: [
          'rgba(75, 192, 192, 1)',
          'rgba(201, 203, 207, 1)'
        ],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `完成度：${((completed / totalTarget) * 100).toFixed(1)}%`,
        position: 'bottom',
        padding: {
          bottom: 10
        },
        font: {
          size: 16,
          weight: 'normal'
        }
      },
    },
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <Pie data={data} options={options} />
      <div style={{ marginTop: '10px', display: 'flex', justifyContent: 'center' }}>
        <p style={{ margin: 0 }}>已完成: {completed}</p>
        <p style={{ margin: '0 0 0 10px' }}>未完成: {remaining}</p>
      </div>
    </div>
  );
};

export default PieChart; 