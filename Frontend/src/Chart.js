import React from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

// 註冊 ChartJS 組件
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const Chart = ({ stats }) => {
  // 确保 labels 始终为 1 到 6
  const labels = ['1', '2', '3', '4', '5', '6'];

  // 使用 stats 数据填充数据集
  const data = {
    labels: labels,
    datasets: [
      {
        label: "分類統計",
        data: [
          stats[1] || 0,
          stats[2] || 0,
          stats[3] || 0,
          stats[4] || 0,
          stats[5] || 0,
          stats[6] || 0,
        ],
        backgroundColor: "rgba(75, 192, 192, 0.6)",
        borderColor: "rgba(75, 192, 192, 1)",
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
      },
      title: {
        display: true,
        text: '分類統計圖表',
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
    scales: {
      y: {
        beginAtZero: true
      }
    }
  };

  return <Bar data={data} options={options} />;
};

export default Chart;
