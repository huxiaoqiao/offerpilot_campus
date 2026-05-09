export interface SkillChange {
  skill: string
  action: string
  reason: string
}

export interface ExperienceRewrite {
  original: string
  rewritten: string
  changes: string[]
}

export interface ResumeSections {
  summary: { content: string; source: string }
  skills: { content: string[]; changes: SkillChange[] }
  experiences: ExperienceRewrite[]
  job_intention: { content: string; source: string }
}

export interface ResumeRewrite {
  job_id: string
  version: number
  sections: ResumeSections
  html_preview: string
}
