'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Model, GenerateRequest } from '@/app/api'
import { audioApi } from '@/app/api'

const generateSchema = z.object({
  model: z.string().min(1),
  prompt: z.string().min(1).max(500),
  duration: z.number().min(1).max(60),
  seed: z.number().int().optional().nullable(),
  temperature: z.number().min(0).max(3),
  top_k: z.number().min(0).max(500),
  top_p: z.number().min(0).max(1),
  cfg_coef: z.number().min(0).max(10),
  stereo: z.boolean(),
  sample_rate: z.number(),
  format: z.enum(['wav', 'mp3']),
})

type GenerateFormData = z.infer<typeof generateSchema>

interface PromptFormProps {
  onSubmit: (data: GenerateRequest) => void
  isGenerating: boolean
}

export default function PromptForm({ onSubmit, isGenerating }: PromptFormProps) {
  const [models, setModels] = useState<Model[]>([])
  const [preset, setPreset] = useState<'cpu' | 'gpu' | 'custom'>('cpu')

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<GenerateFormData>({
    resolver: zodResolver(generateSchema),
    defaultValues: {
      model: 'musicgen-small',
      prompt: '',
      duration: 10,
      seed: null,
      temperature: 1.0,
      top_k: 250,
      top_p: 0.0,
      cfg_coef: 3.0,
      stereo: true,
      sample_rate: 32000,
      format: 'wav',
    },
  })

  useEffect(() => {
    audioApi.getModels().then(setModels)
  }, [])

  const applyPreset = (presetType: 'cpu' | 'gpu') => {
    setPreset(presetType)
    if (presetType === 'cpu') {
      setValue('model', 'musicgen-small')
      setValue('duration', 10)
      setValue('temperature', 1.0)
      setValue('top_k', 250)
      setValue('cfg_coef', 2.0)
      setValue('stereo', false)
      setValue('sample_rate', 32000)
    } else if (presetType === 'gpu') {
      setValue('model', 'musicgen-medium')
      setValue('duration', 30)
      setValue('temperature', 1.0)
      setValue('top_k', 250)
      setValue('cfg_coef', 3.5)
      setValue('stereo', true)
      setValue('sample_rate', 32000)
    }
  }

  const onFormSubmit = (data: GenerateFormData) => {
    onSubmit(data as GenerateRequest)
  }

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
      {/* Presets */}
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => applyPreset('cpu')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
            preset === 'cpu'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
          }`}
        >
          ⚡ Rapido (CPU)
        </button>
        <button
          type="button"
          onClick={() => applyPreset('gpu')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
            preset === 'gpu'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
          }`}
        >
          🎨 Qualità (GPU)
        </button>
      </div>

      {/* Model */}
      <div>
        <label className="block text-sm font-medium mb-2">Modello</label>
        <select
          {...register('model')}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
          disabled={isGenerating}
        >
          {models.map((model) => (
            <option key={model.id} value={model.id}>
              {model.name} - {model.description}
            </option>
          ))}
        </select>
        {errors.model && (
          <p className="text-red-500 text-sm mt-1">{errors.model.message}</p>
        )}
      </div>

      {/* Prompt */}
      <div>
        <label className="block text-sm font-medium mb-2">Prompt Testuale</label>
        <textarea
          {...register('prompt')}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
          placeholder="es: cinematic ambient with evolving pads and subtle percussion"
          disabled={isGenerating}
        />
        {errors.prompt && (
          <p className="text-red-500 text-sm mt-1">{errors.prompt.message}</p>
        )}
      </div>

      {/* Quick Prompts */}
      <details className="border border-gray-300 dark:border-gray-600 rounded-lg p-4">
        <summary className="cursor-pointer font-medium mb-2">🎨 Prompt Rapidi</summary>
        <div className="mt-4 space-y-4">
          <div>
            <h4 className="text-sm font-semibold mb-2">🌫️ Ambienti e spazi</h4>
            <div className="grid grid-cols-1 gap-2">
              {[
                "vento che passa attraverso tubi metallici in un tunnel sotterraneo umido",
                "stanze di un edificio abbandonato che risuonano lentamente, eco lunga e spettrale",
                "onde che si infrangono su rocce vulcaniche, con spruzzi e profondità subacquee",
                "intercapedine meccanica di un'astronave in standby, vibrazioni basse e regolari",
                "pioggia fine che cade su superfici di plastica e metallo, con risonanze irregolari"
              ].map((prompt, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setValue('prompt', prompt)}
                  disabled={isGenerating}
                  className="text-left px-3 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition text-gray-700 dark:text-gray-300 disabled:opacity-50"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="text-sm font-semibold mb-2">⚙️ Tessiture meccaniche e tecnologiche</h4>
            <div className="grid grid-cols-1 gap-2">
              {[
                "rotazione lenta di un motore elettrico difettoso, con rumori di contatto e interferenze radio",
                "stampante 3D che lavora su un materiale liquido, gocciolii e micro-click digitali",
                "pannello di controllo che si accende, bip elettronici, ventole e rumore termico",
                "rete dati analogica che trasmette pacchetti sonori, modulazioni glitch e disturbi di linea",
                "campo magnetico pulsante, con riverbero metallico e scariche elettriche intermittenti"
              ].map((prompt, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setValue('prompt', prompt)}
                  disabled={isGenerating}
                  className="text-left px-3 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition text-gray-700 dark:text-gray-300 disabled:opacity-50"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          <div>
            <h4 className="text-sm font-semibold mb-2">🌿 Materia e natura astratta</h4>
            <div className="grid grid-cols-1 gap-2">
              {[
                "foglie bagnate che vengono calpestate lentamente, con suono vicino e dettagliato",
                "ghiaccio che si frattura in una grotta, rumori sordi e micro-screpolature cristalline",
                "movimento viscoso di una sostanza gelatinosa che scorre su vetro",
                "ragnatela che vibra nel vento amplificata mille volte, filamenti che risuonano",
                "sabbia trascinata dal vento con granelli che si urtano e cambiano frequenza"
              ].map((prompt, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setValue('prompt', prompt)}
                  disabled={isGenerating}
                  className="text-left px-3 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition text-gray-700 dark:text-gray-300 disabled:opacity-50"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          <div>
            <h4 className="text-sm font-semibold mb-2">🧠 Psicogeografie sonore</h4>
            <div className="grid grid-cols-1 gap-2">
              {[
                "campo elettromagnetico tradotto in suono, onde pulsanti e variazioni lente di frequenza",
                "eco di pensieri in una stanza vuota, come voci ovattate che si dissolvono nel silenzio",
                "desincronizzazione temporale: un battito che si sdoppia e si ricompone lentamente",
                "respiri meccanici alternati a rumori liquidi, come un polmone artificiale immerso",
                "spazio sonoro impossibile: materiali solidi che vibrano come fluidi, armonici caotici e microimpatti"
              ].map((prompt, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setValue('prompt', prompt)}
                  disabled={isGenerating}
                  className="text-left px-3 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition text-gray-700 dark:text-gray-300 disabled:opacity-50"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        </div>
      </details>

      {/* Duration */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Durata: {watch('duration')}s
        </label>
        <input
          type="range"
          {...register('duration', { valueAsNumber: true })}
          min="1"
          max="60"
          className="w-full"
          disabled={isGenerating}
        />
        {errors.duration && (
          <p className="text-red-500 text-sm mt-1">{errors.duration.message}</p>
        )}
      </div>

      {/* Advanced Parameters */}
      <details className="border border-gray-300 dark:border-gray-600 rounded-lg p-4">
        <summary className="cursor-pointer font-medium">Parametri Avanzati</summary>
        <div className="mt-4 grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Seed (opzionale)</label>
            <input
              type="number"
              {...register('seed', { valueAsNumber: true })}
              placeholder="-1 = random"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
              disabled={isGenerating}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Temperature</label>
            <input
              type="number"
              step="0.1"
              {...register('temperature', { valueAsNumber: true })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
              disabled={isGenerating}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Top-K</label>
            <input
              type="number"
              {...register('top_k', { valueAsNumber: true })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
              disabled={isGenerating}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Top-P</label>
            <input
              type="number"
              step="0.1"
              {...register('top_p', { valueAsNumber: true })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
              disabled={isGenerating}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">CFG Coefficient</label>
            <input
              type="number"
              step="0.1"
              {...register('cfg_coef', { valueAsNumber: true })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
              disabled={isGenerating}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Sample Rate</label>
            <select
              {...register('sample_rate', { valueAsNumber: true })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
              disabled={isGenerating}
            >
              <option value={16000}>16 kHz</option>
              <option value={32000}>32 kHz</option>
              <option value={44100}>44.1 kHz</option>
              <option value={48000}>48 kHz</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              {...register('stereo')}
              className="w-4 h-4"
              disabled={isGenerating}
            />
            <label className="text-sm font-medium">Stereo</label>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Formato</label>
            <select
              {...register('format')}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
              disabled={isGenerating}
            >
              <option value="wav">WAV</option>
              <option value="mp3">MP3</option>
            </select>
          </div>
        </div>
      </details>

      {/* Submit */}
      <button
        type="submit"
        disabled={isGenerating}
        className="w-full px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        {isGenerating ? '⏳ Generazione in corso...' : '🎵 Genera Audio'}
      </button>
    </form>
  )
}

