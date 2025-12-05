'use client'

import { useEffect, useState } from 'react'
import { JobStatus } from '@/app/api'
import { audioApi } from '@/app/api'

interface JobProgressProps {
  jobId: string
  onComplete: (resultUrl: string | null) => void
  onError: (error: string) => void
}

export default function JobProgress({ jobId, onComplete, onError }: JobProgressProps) {
  const [status, setStatus] = useState<JobStatus | null>(null)

  useEffect(() => {
    let eventSource: EventSource | null = null
    let pollInterval: NodeJS.Timeout | null = null

    // Try SSE first
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      eventSource = new EventSource(`${apiUrl}/api/jobs/${jobId}/events`)

      const handleSSEMessage = (event: MessageEvent) => {
        try {
          // Skip if data is empty
          if (!event.data || event.data.trim() === '') {
            return
          }

          const data = JSON.parse(event.data)
          setStatus(data)

          if (data.status === 'done') {
            onComplete(data.result_url)
            eventSource?.close()
          } else if (data.status === 'error') {
            onError(data.error || 'Unknown error')
            eventSource?.close()
          }
        } catch (e) {
          // Silently ignore parse errors - might be connection messages
          console.debug('SSE message parse:', event.data, e)
        }
      }

      // Handle default messages
      eventSource.onmessage = handleSSEMessage

      // Handle progress events
      eventSource.addEventListener('progress', handleSSEMessage)

      eventSource.onerror = () => {
        // If connection error, fallback to polling
        eventSource?.close()
        startPolling()
      }
    } catch (e) {
      console.warn('SSE not available, using polling:', e)
      startPolling()
    }

    function startPolling() {
      pollInterval = setInterval(async () => {
        try {
          const jobStatus = await audioApi.getJobStatus(jobId)
          setStatus(jobStatus)

          if (jobStatus.status === 'done') {
            onComplete(jobStatus.result_url)
          } else if (jobStatus.status === 'error') {
            onError(jobStatus.error || 'Unknown error')
          }
        } catch (e) {
          console.error('Failed to poll job status:', e)
        }
      }, 1000)
    }

    return () => {
      eventSource?.close()
      if (pollInterval) clearInterval(pollInterval)
    }
  }, [jobId, onComplete, onError])

  if (!status) {
    return <div className="text-center py-8">Caricamento stato...</div>
  }

  const getStatusColor = () => {
    switch (status.status) {
      case 'queued':
        return 'bg-gray-400'
      case 'running':
        return 'bg-blue-500'
      case 'done':
        return 'bg-green-500'
      case 'error':
        return 'bg-red-500'
      default:
        return 'bg-gray-400'
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">
          Stato: <span className={`px-2 py-1 rounded text-white ${getStatusColor()}`}>
            {status.status}
          </span>
        </span>
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {status.progress}%
        </span>
      </div>

      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
        <div
          className="bg-primary-600 h-full transition-all duration-300 ease-out"
          style={{ width: `${status.progress}%` }}
        />
      </div>

      {status.message && (
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {status.message}
        </p>
      )}

      {status.status === 'running' && (
        <div className="text-xs text-gray-500 dark:text-gray-500">
          Tempo stimato: ~{Math.ceil((100 - status.progress) * 0.2)}s rimanenti
        </div>
      )}
    </div>
  )
}

