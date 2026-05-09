export interface JobPost {
  id: string
  company_name: string
  position_title: string
  jd_raw_text: string
  responsibilities: string[]
  hard_requirements: string[]
  soft_requirements: string[]
  salary_min: number | null
  salary_max: number | null
  city: string
  industry: string
  keywords: string[]
  source_url: string | null
  quality_score: number
  quality_details: Record<string, number>
  risk_tags: string[]
  is_duplicate: boolean
  duplicate_of: string | null
  status: string
  created_at: string
  updated_at: string
}

export interface JobCreate {
  jd_text: string
  company_name?: string
  position_title?: string
  source_url?: string
}

export interface JobBatchCreate {
  jobs: JobCreate[]
}
