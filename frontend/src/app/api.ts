import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface Model {
  id: string
  name: string
  type: string
  description: string
  supports_stereo: boolean
  sample_rate: number
  requires_gpu: boolean
}

export interface GenerateRequest {
  model: string
  prompt: string
  duration: number
  seed?: number | null
  temperature: number
  top_k: number
  top_p: number
  cfg_coef: number
  stereo: boolean
  sample_rate: number
  format: string
}

export interface GenerateResponse {
  job_id: string
  status: string
  estimated_seconds: number
  rate_limit_remaining: number
}

export interface JobStatus {
  job_id: string
  status: 'queued' | 'running' | 'done' | 'error'
  progress: number
  message: string
  result_url: string | null
  error: string | null
  params: GenerateRequest
  created_at: string
  started_at: string | null
  completed_at: string | null
}

export const audioApi = {
  async getModels(): Promise<Model[]> {
    const response = await api.get<{ models: Model[] }>('/api/models')
    return response.data.models
  },

  async generateAudio(params: GenerateRequest): Promise<GenerateResponse> {
    const response = await api.post<GenerateResponse>('/api/generate', params)
    return response.data
  },

  async getJobStatus(jobId: string): Promise<JobStatus> {
    const response = await api.get<JobStatus>(`/api/jobs/${jobId}`)
    return response.data
  },

  getFileUrl(filename: string): string {
    return `${API_BASE_URL}/api/files/${filename}`
  },
}

