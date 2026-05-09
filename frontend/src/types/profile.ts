export interface Education {
  school: string
  major: string
  degree: string
  start_date: string
  end_date: string
  gpa?: string
}

export interface Experience {
  type: string
  title: string
  organization: string
  start_date: string
  end_date: string
  description: string
  achievements: string[]
  technologies: string[]
}

export interface StructuredResume {
  education: Education[]
  skills: string[]
  experiences: Experience[]
  honors: string[]
  self_intro: string
}

export interface Profile {
  id: string
  name: string
  school: string
  major: string
  grade: string
  graduation_year: number
  target_positions: string[]
  target_cities: string[]
  salary_min: number | null
  salary_max: number | null
  target_industries: string[]
  avoid_items: string[]
  resume_raw_text: string
  resume_structured: StructuredResume | null
  skill_ratings: Record<string, number>
  created_at: string
  updated_at: string
}

export interface ProfileCreate {
  name: string
  school: string
  major: string
  grade: string
  graduation_year: number
  target_positions?: string[]
  target_cities?: string[]
  salary_min?: number
  salary_max?: number
  target_industries?: string[]
  avoid_items?: string[]
}

export interface ProfileUpdate {
  name?: string
  school?: string
  major?: string
  grade?: string
  graduation_year?: number
  target_positions?: string[]
  target_cities?: string[]
  salary_min?: number | null
  salary_max?: number | null
  target_industries?: string[]
  avoid_items?: string[]
}
