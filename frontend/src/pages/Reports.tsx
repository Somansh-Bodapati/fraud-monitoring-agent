import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { format } from 'date-fns'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function Reports() {
  const { data, isLoading } = useQuery({
    queryKey: ['reports'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/reports`)
      return response.data
    },
  })

  if (isLoading) {
    return <div className="text-center py-8">Loading reports...</div>
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Reports</h1>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {data?.map((report: any) => (
            <li key={report.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">
                      {report.report_type.charAt(0).toUpperCase() +
                        report.report_type.slice(1)}{' '}
                      Report
                    </h3>
                    <p className="mt-1 text-sm text-gray-500">
                      {format(new Date(report.start_date), 'MMM dd, yyyy')} -{' '}
                      {format(new Date(report.end_date), 'MMM dd, yyyy')}
                    </p>
                    {report.summary && (
                      <p className="mt-2 text-sm text-gray-700">{report.summary}</p>
                    )}
                  </div>
                  <div className="text-sm text-gray-500">
                    {format(new Date(report.created_at), 'MMM dd, yyyy')}
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

