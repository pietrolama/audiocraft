'use client'

import { useEffect, useState } from 'react'
import { openDB, DBSchema, IDBPDatabase } from 'idb'

interface HistoryItem {
  id: string
  jobId: string
  prompt: string
  model: string
  duration: number
  resultUrl: string | null
  createdAt: string
}

interface AudioCraftDB extends DBSchema {
  history: {
    key: string
    value: HistoryItem
    indexes: { 'by-date': string }
  }
}

export default function HistoryPanel() {
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      const db = await openDB<AudioCraftDB>('audiocraft-db', 1, {
        upgrade(db) {
          const store = db.createObjectStore('history', { keyPath: 'id' })
          store.createIndex('by-date', 'createdAt')
        },
      })

      const items = await db.getAll('history')
      setHistory(items.sort((a, b) => 
        new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      ))
    } catch (e) {
      console.error('Failed to load history:', e)
    }
  }

  const clearHistory = async () => {
    try {
      const db = await openDB<AudioCraftDB>('audiocraft-db', 1)
      await db.clear('history')
      setHistory([])
    } catch (e) {
      console.error('Failed to clear history:', e)
    }
  }

  // Listen for new history items
  useEffect(() => {
    const handleStorageChange = () => {
      loadHistory()
    }

    window.addEventListener('history-updated', handleStorageChange)
    return () => window.removeEventListener('history-updated', handleStorageChange)
  }, [])

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-4 right-4 px-4 py-2 bg-primary-600 text-white rounded-lg shadow-lg hover:bg-primary-700 transition z-50"
      >
        📜 Cronologia ({history.length})
      </button>

      {isOpen && (
        <div className="fixed bottom-20 right-4 w-96 max-h-96 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-xl z-50 overflow-hidden flex flex-col">
          <div className="p-4 border-b border-gray-300 dark:border-gray-600 flex justify-between items-center">
            <h3 className="font-semibold">Cronologia</h3>
            <div className="flex gap-2">
              <button
                onClick={clearHistory}
                className="text-sm text-red-600 hover:text-red-700"
              >
                Cancella
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="text-sm text-gray-600 dark:text-gray-400"
              >
                ✕
              </button>
            </div>
          </div>

          <div className="overflow-y-auto flex-1 p-2">
            {history.length === 0 ? (
              <p className="text-center text-gray-500 dark:text-gray-400 py-8 text-sm">
                Nessun elemento in cronologia
              </p>
            ) : (
              <div className="space-y-2">
                {history.map((item) => (
                  <div
                    key={item.id}
                    className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition"
                  >
                    <p className="text-sm font-medium truncate">{item.prompt}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {item.model} • {item.duration}s
                    </p>
                    {item.resultUrl && (
                      <a
                        href={`http://localhost:8000${item.resultUrl}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-primary-600 hover:underline"
                      >
                        Ascolta →
                      </a>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  )
}

