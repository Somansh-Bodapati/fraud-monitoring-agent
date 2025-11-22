import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function Alerts() {
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/alerts`)
      return response.data
    },
  })

  const markReadMutation = useMutation({
    mutationFn: async (alertId: number) => {
      await axios.patch(`${API_URL}/api/alerts/${alertId}/read`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      toast.success('Alert marked as read')
    },
  })

  if (isLoading) {
    return <div className="text-center py-8">Loading alerts...</div>
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800'
      case 'high':
        return 'bg-orange-100 text-orange-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-blue-100 text-blue-800'
    }
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Alerts</h1>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {data?.map((alert: any) => (
            <li key={alert.id} className={!alert.is_read ? 'bg-yellow-50' : ''}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <h3 className="text-sm font-medium text-gray-900">
                        {alert.title}
                      </h3>
                      <span
                        className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(
                          alert.severity
                        )}`}
                      >
                        {alert.severity}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-gray-500">{alert.message}</p>
                    {alert.recommendation && (
                      <p className="mt-1 text-sm text-blue-600">
                        {alert.recommendation}
                      </p>
                    )}
                    <p className="mt-1 text-xs text-gray-400">
                      {format(new Date(alert.created_at), 'MMM dd, yyyy HH:mm')}
                    </p>
                  </div>
                  <div className="ml-4">
                    {!alert.is_read && (
                      <button
                        onClick={() => markReadMutation.mutate(alert.id)}
                        className="text-sm text-blue-600 hover:text-blue-800"
                      >
                        Mark as read
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

