'use client'

import { useState, useEffect } from 'react'
import PromptForm from '@/components/PromptForm'
import JobProgress from '@/components/JobProgress'
import AudioPlayerCard from '@/components/AudioPlayerCard'
import HistoryPanel from '@/components/HistoryPanel'
import { GenerateRequest, JobStatus } from './api'
import { audioApi } from './api'
import { openDB, DBSchema } from 'idb'

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

export default function Home() {
  const [currentJobId, setCurrentJobId] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [resultUrl, setResultUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [currentParams, setCurrentParams] = useState<GenerateRequest | null>(null)
  const [darkMode, setDarkMode] = useState(false)

  const saveToHistory = async (item: HistoryItem) => {
    try {
      const db = await openDB<AudioCraftDB>('audiocraft-db', 1, {
        upgrade(db) {
          const store = db.createObjectStore('history', { keyPath: 'id' })
          store.createIndex('by-date', 'createdAt')
        },
      })

      await db.put('history', item)
      window.dispatchEvent(new Event('history-updated'))
    } catch (e) {
      console.error('Failed to save to history:', e)
    }
  }

  const handleGenerate = async (data: GenerateRequest) => {
    try {
      setError(null)
      setResultUrl(null)
      setIsGenerating(true)
      setCurrentParams(data)

      const response = await audioApi.generateAudio(data)
      setCurrentJobId(response.job_id)
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || 'Errore nella generazione')
      setIsGenerating(false)
    }
  }

  const handleJobComplete = async (url: string | null) => {
    setIsGenerating(false)
    setResultUrl(url)
    
    if (currentParams && url) {
      await saveToHistory({
        id: `${Date.now()}-${Math.random()}`,
        jobId: currentJobId || '',
        prompt: currentParams.prompt,
        model: currentParams.model,
        duration: currentParams.duration,
        resultUrl: url,
        createdAt: new Date().toISOString(),
      })
    }
  }

  const handleJobError = (err: string) => {
    setIsGenerating(false)
    setError(err)
  }

  useEffect(() => {
    // Check for dark mode preference
    const isDark = localStorage.getItem('darkMode') === 'true' ||
      (!localStorage.getItem('darkMode') && window.matchMedia('(prefers-color-scheme: dark)').matches)
    
    setDarkMode(isDark)
    if (isDark) {
      document.documentElement.classList.add('dark')
    }
  }, [])

  const toggleDarkMode = () => {
    const newMode = !darkMode
    setDarkMode(newMode)
    localStorage.setItem('darkMode', String(newMode))
    if (newMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              🎵 AudioCraft Generator
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Genera audio da testo con Meta AudioCraft
            </p>
          </div>
          <button
            onClick={toggleDarkMode}
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition"
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="grid md:grid-cols-2 gap-8">
          {/* Left Column: Form */}
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Parametri Generazione</h2>
              <PromptForm onSubmit={handleGenerate} isGenerating={isGenerating} />
            </div>
          </div>

          {/* Right Column: Progress & Results */}
          <div className="space-y-6">
            {/* Progress */}
            {currentJobId && isGenerating && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-semibold mb-4">Progresso</h2>
                <JobProgress
                  jobId={currentJobId}
                  onComplete={handleJobComplete}
                  onError={handleJobError}
                />
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <p className="text-red-800 dark:text-red-200">❌ {error}</p>
              </div>
            )}

            {/* Result */}
            {resultUrl && currentParams && (
              <AudioPlayerCard resultUrl={resultUrl} params={currentParams} />
            )}
          </div>
        </div>
      </main>

      {/* History Panel */}
      <HistoryPanel />
    </div>
  )
}

