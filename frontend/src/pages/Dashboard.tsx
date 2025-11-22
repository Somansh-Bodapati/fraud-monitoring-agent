import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Doughnut, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
} from 'chart.js'

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title
)

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function Dashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/dashboard/stats`)
      return response.data
    },
  })

  const { data: transactionsData } = useQuery({
    queryKey: ['transactions'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/transactions`)
      return response.data
    },
  })

  if (isLoading) {
    return <div className="text-center py-8">Loading dashboard...</div>
  }

  // Category breakdown pie chart
  const categoryBreakdown = data?.category_breakdown || {}
  const categoryLabels = Object.keys(categoryBreakdown).map((key) => key || 'uncategorized')
  const categoryValues = Object.values(categoryBreakdown).map((c: any) => c?.total || 0)

  const categoryData = {
    labels: categoryLabels,
    datasets: [
      {
        data: categoryValues,
        backgroundColor: [
          '#3B82F6',
          '#10B981',
          '#F59E0B',
          '#EF4444',
          '#8B5CF6',
          '#EC4899',
          '#06B6D4',
          '#84CC16',
          '#F97316',
          '#A855F7',
        ],
      },
    ],
  }

  // High amount transactions (top 10)
  const highAmountTransactions = transactionsData
    ? [...transactionsData]
        .sort((a: any, b: any) => b.amount - a.amount)
        .slice(0, 10)
    : []

  const highAmountData = {
    labels: highAmountTransactions.map((t: any) =>
      (t.merchant || t.description || 'Unknown').substring(0, 20)
    ),
    datasets: [
      {
        label: 'Amount ($)',
        data: highAmountTransactions.map((t: any) => t.amount),
        backgroundColor: '#3B82F6',
      },
    ],
  }

  // Calculate high amount threshold (transactions above average)
  const avgAmount =
    transactionsData && transactionsData.length > 0
      ? transactionsData.reduce((sum: number, t: any) => sum + t.amount, 0) /
        transactionsData.length
      : 0

  const highAmountCount =
    transactionsData?.filter((t: any) => t.amount > avgAmount * 1.5).length || 0

  const pendingCount = transactionsData?.filter((t: any) => t.status === 'pending').length || 0

  return (
    <div className="px-4 py-6 sm:px-0">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="text-2xl font-bold text-gray-900">
                  {data?.transactions?.total || 0}
                </div>
                <div className="text-sm text-gray-500">Total Transactions</div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="text-2xl font-bold text-gray-900">
                  ${(data?.transactions?.total_amount || 0).toFixed(2)}
                </div>
                <div className="text-sm text-gray-500">Total Amount</div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="text-2xl font-bold text-red-600">
                  {data?.transactions?.anomalies || 0}
                </div>
                <div className="text-sm text-gray-500">Anomalies</div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="text-2xl font-bold text-yellow-600">
                  {data?.alerts?.unread || 0}
                </div>
                <div className="text-sm text-gray-500">Unread Alerts</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Category Spending Breakdown</h2>
          {categoryLabels.length > 0 ? (
            <div className="h-64">
              <Doughnut
                data={categoryData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'right',
                    },
                    tooltip: {
                      callbacks: {
                        label: function (context) {
                          const label = context.label || ''
                          const value = context.parsed || 0
                          const total = context.dataset.data.reduce(
                            (a: number, b: number) => a + b,
                            0
                          )
                          const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0
                          return `${label}: $${value.toFixed(2)} (${percentage}%)`
                        },
                      },
                    },
                  },
                }}
              />
            </div>
          ) : (
            <p className="text-gray-500">No category data available</p>
          )}
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Top High Amount Transactions</h2>
          {highAmountTransactions.length > 0 ? (
            <div className="h-64">
              <Bar
                data={highAmountData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      display: false,
                    },
                    tooltip: {
                      callbacks: {
                        label: function (context) {
                          return `$${context.parsed.y.toFixed(2)}`
                        },
                      },
                    },
                  },
                  scales: {
                    y: {
                      beginAtZero: true,
                      ticks: {
                        callback: function (value) {
                          return '$' + value
                        },
                      },
                    },
                  },
                }}
              />
            </div>
          ) : (
            <p className="text-gray-500">No transaction data available</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">High Amount Transactions</h2>
          <div className="text-3xl font-bold text-blue-600 mb-2">
            {highAmountCount}
          </div>
          <p className="text-sm text-gray-600">
            Transactions above ${(avgAmount * 1.5).toFixed(2)} (1.5x average)
          </p>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Flagged Transactions</span>
              <span className="text-sm font-semibold">
                {data?.transactions?.flagged || 0}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Total Alerts</span>
              <span className="text-sm font-semibold">
                {data?.alerts?.total || 0}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Pending Approval</span>
              <span className="text-sm font-semibold text-yellow-600">
                {pendingCount}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Average Transaction</h2>
          <div className="text-3xl font-bold text-gray-900 mb-2">
            ${avgAmount.toFixed(2)}
          </div>
          <p className="text-sm text-gray-600">
            Based on {transactionsData?.length || 0} transactions
          </p>
        </div>
      </div>
    </div>
  )
}
