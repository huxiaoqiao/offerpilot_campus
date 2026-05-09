export interface TimelineEntry {
  time: string
  action: string
  detail: string
}

export interface Application {
  id: string
  job_id: string
  job_title: string
  company_name: string
  status: string
  match_score: number | null
  next_action: string | null
  next_action_deadline: string | null
  notes: string
  tags: string[]
  timeline: TimelineEntry[]
  created_at: string
  updated_at: string
}

export interface ApplicationCreate {
  job_id: string
  job_title: string
  company_name: string
  status?: string
  match_score?: number | null
  next_action?: string | null
  next_action_deadline?: string | null
  notes?: string
  tags?: string[]
}

export interface BoardStats {
  total: number
  by_status: Record<string, number>
  avg_match_score: number
  offer_rate: number
  interview_rate: number
  top_dimension_scores: Record<string, number>
}
