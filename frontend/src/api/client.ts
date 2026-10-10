import type {
  AnalyzeResponse,
  AskRequest,
  AskResponse,
  ChartType,
  CompareResponse,
} from './types'
import { mockAnalyze, mockAsk, mockCompare } from './mock'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'
const BASE = '/api'

async function handle<T>(res: Response): Promise<T> {
  if (res.ok) return (await res.json()) as T
  let message = `Request failed (${res.status})`
  try {
    const body = await res.json()
    if (typeof body.detail === 'string') message = body.detail
  } catch {
    // keep the default message
  }
  throw new Error(message)
}

export const isMockMode = USE_MOCK

export async function health(): Promise<{ status: string; model_loaded: boolean }> {
  if (USE_MOCK) return { status: 'ok', model_loaded: true }
  return handle(await fetch(`${BASE}/health`))
}

export async function analyze(image: File, chartType: ChartType = 'auto'): Promise<AnalyzeResponse> {
  if (USE_MOCK) return mockAnalyze(image)
  const form = new FormData()
  form.append('image', image)
  form.append('chart_type', chartType)
  return handle(await fetch(`${BASE}/analyze`, { method: 'POST', body: form }))
}

export async function ask(req: AskRequest): Promise<AskResponse> {
  if (USE_MOCK) return mockAsk(req)
  return handle(
    await fetch(`${BASE}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    }),
  )
}

export async function compare(image: File): Promise<CompareResponse> {
  if (USE_MOCK) return mockCompare(image)
  const form = new FormData()
  form.append('image', image)
  return handle(await fetch(`${BASE}/compare`, { method: 'POST', body: form }))
}
