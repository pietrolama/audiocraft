'use client'

import { useState } from 'react'
import { audioApi } from '@/app/api'

interface AudioPlayerCardProps {
  resultUrl: string | null
  params: {
    prompt: string
    model: string
    duration: number
  }
}

export default function AudioPlayerCard({ resultUrl, params }: AudioPlayerCardProps) {
  const [isPlaying, setIsPlaying] = useState(false)

  if (!resultUrl) {
    return null
  }

  const filename = resultUrl.split('/').pop() || 'audio.wav'
  const audioUrl = audioApi.getFileUrl(filename)

  const handleDownload = () => {
    const link = document.createElement('a')
    link.href = audioUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="border border-gray-300 dark:border-gray-600 rounded-lg p-6 space-y-4 bg-white dark:bg-gray-800">
      <h3 className="text-lg font-semibold">🎵 Audio Generato</h3>

      <div className="space-y-2">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          <strong>Prompt:</strong> {params.prompt}
        </p>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          <strong>Modello:</strong> {params.model}
        </p>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          <strong>Durata:</strong> {params.duration}s
        </p>
      </div>

      <audio
        controls
        className="w-full"
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onEnded={() => setIsPlaying(false)}
      >
        <source src={audioUrl} type="audio/wav" />
        <source src={audioUrl} type="audio/mpeg" />
        Il tuo browser non supporta l'elemento audio.
      </audio>

      <button
        onClick={handleDownload}
        className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium"
      >
        ⬇️ Scarica {filename}
      </button>
    </div>
  )
}

