"use client";

import { useState } from "react";
import { Bar, Doughnut, Radar, Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  RadialLinearScale,
  TimeScale,
} from "chart.js";
import "chartjs-adapter-date-fns";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  PointElement,
  LineElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

export default function VisualizeData() {
  const [chartData, setChartData] = useState<any>(null);
  const [doughnutData, setDoughnutData] = useState<any>(null);
  const [radarData, setRadarData] = useState<any>(null);
  const [lineData, setLineData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [noData, setNoData] = useState(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setNoData(false);

    try {
      const response = await fetch(`http://127.0.0.1:5000/get_transactions`, {
        method: "GET",
        credentials: "include",
      });

      if (!response.ok) throw new Error("Failed to fetch transactions");

      const data = await response.json();
      const transactions = data.transactions;
      if (!transactions || transactions.length === 0) {
        setNoData(true);
        setLoading(false);
        return;
      }

      const categories = [...new Set(transactions.map((item: any) => item.category))];
      const categoryAmounts = categories.map((cat) =>
        transactions
          .filter((item: any) => item.category === cat)
          .reduce((sum, item) => sum + parseFloat(item.amount), 0)
      );

      // Bar, Doughnut, Radar setup
      setChartData({
        labels: categories,
        datasets: [
          {
            label: "Amount",
            data: categoryAmounts,
            backgroundColor: "rgba(255, 99, 132, 0.6)",
            borderColor: "rgba(255, 99, 132, 1)",
            borderWidth: 1,
          },
        ],
      });

      setDoughnutData({
        labels: categories,
        datasets: [
          {
            data: categoryAmounts,
            backgroundColor: ["#FF5733", "#33FF57", "#3357FF", "#FFC300", "#C70039", "#9370DB"],
          },
        ],
      });

      setRadarData({
        labels: categories,
        datasets: [
          {
            label: "Spending Pattern",
            data: categoryAmounts,
            backgroundColor: "rgba(255, 99, 132, 0.2)",
            borderColor: "rgba(255, 99, 132, 1)",
            pointBackgroundColor: "rgba(255, 99, 132, 1)",
          },
        ],
      });

      // Line Chart: one line per category
      const categoryDateMap: Record<string, Record<string, number>> = {};
      const allDatesSet = new Set<string>();

      transactions.forEach((item: any) => {
        const date = new Date(item.date).toISOString().split("T")[0];
        const category = item.category;
        const amount = parseFloat(item.amount);

        allDatesSet.add(date);
        if (!categoryDateMap[category]) categoryDateMap[category] = {};
        categoryDateMap[category][date] = (categoryDateMap[category][date] || 0) + amount;
      });

      const allDates = Array.from(allDatesSet).sort();
      const colorPalette = [
        "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40",
        "#8E44AD", "#1ABC9C", "#F39C12", "#2ECC71"
      ];

      const lineDatasets = Object.keys(categoryDateMap).map((category, i) => ({
        label: category,
        data: allDates.map((date) => categoryDateMap[category][date] || 0),
        borderColor: colorPalette[i % colorPalette.length],
        backgroundColor: colorPalette[i % colorPalette.length],
        tension: 0.4,
        fill: false,
        pointRadius: 5,
      }));

      setLineData({
        labels: allDates,
        datasets: lineDatasets,
      });

      setLoading(false);
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-8 text-center text-indigo-800">
        Visualize Data
      </h1>

      <form
        onSubmit={handleSubmit}
        className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4"
      >
        <div className="flex items-center justify-center">
          <button
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded"
            type="submit"
          >
            {loading ? "Loading..." : "Visualize"}
          </button>
        </div>
      </form>

      {error && <p className="text-red-500 text-center">{error}</p>}
      {noData && (
        <p className="text-gray-600 text-center">No transactions found.</p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {chartData && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-center text-lg font-bold mb-2">Bar Chart</h2>
            <Bar data={chartData} />
          </div>
        )}
        {doughnutData && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-center text-lg font-bold mb-2">Doughnut Chart</h2>
            <Doughnut data={doughnutData} />
          </div>
        )}
        {radarData && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-center text-lg font-bold mb-2">Radar Chart</h2>
            <Radar data={radarData} />
          </div>
        )}
        {lineData && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-center text-lg font-bold mb-2">Line Chart</h2>
            <Line
              data={lineData}
              options={{
                plugins: {
                  tooltip: {
                    mode: "index",
                    intersect: false,
                    callbacks: {
                      label: function (context) {
                        return `${context.dataset.label}: $${context.formattedValue}`;
                      },
                    },
                  },
                },
                scales: {
                  x: { title: { display: true, text: "Date" } },
                  y: { title: { display: true, text: "Amount ($)" }, beginAtZero: true },
                },
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
