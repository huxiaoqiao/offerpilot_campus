export interface DimensionScore {
  score: number
  detail: string
}

export interface MatchedEvidence {
  jd_requirement: string
  resume_evidence: string
  evidence_source: string
  strength: string
}

export interface Gap {
  jd_requirement: string
  severity: string
  suggestion: string
}

export interface Risk {
  risk: string
  level: string
  mitigation: string
}

export interface MatchResult {
  job_id: string
  total_score: number
  opportunity_level: string
  dimension_scores: Record<string, DimensionScore>
  matched_evidence: MatchedEvidence[]
  gaps: Gap[]
  risks: Risk[]
  improvement_actions: string[]
}
