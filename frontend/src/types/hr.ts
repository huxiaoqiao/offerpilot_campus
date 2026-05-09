export interface ATSCheck {
  keyword_match_rate: number
  format_compliance: boolean
  readability_score: number
  issues: string[]
}

export interface ScreeningResult {
  pass_probability: number
  pass_reasons: string[]
  fail_reasons: string[]
}

export interface HRFeedback {
  category: string
  feedback: string
  priority: string
}

export interface HRSimulation {
  job_id: string
  ats_check: ATSCheck
  screening_result: ScreeningResult
  hr_feedback: HRFeedback[]
}
