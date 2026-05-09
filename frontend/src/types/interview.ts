export interface InterviewQuestion {
  id: string
  category: string
  question: string
  reference_answer_framework: string
  related_resume_item: string | null
  related_risk: string | null
}

export interface STARStory {
  title: string
  situation: string
  task: string
  action: string
  result: string
  applicable_questions: string[]
}

export interface RiskFollowup {
  risk: string
  possible_question: string
  suggested_answer: string
}

export interface InterviewData {
  job_id: string
  questions: InterviewQuestion[]
  star_stories: STARStory[]
  risk_followups: RiskFollowup[]
}
