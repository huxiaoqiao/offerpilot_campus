import { Chip } from '@mui/material'

interface ScoreBadgeProps {
  score: number
  label?: string
}

function getScoreColor(score: number): 'success' | 'primary' | 'warning' | 'error' {
  if (score >= 80) return 'success'
  if (score >= 60) return 'primary'
  if (score >= 40) return 'warning'
  return 'error'
}

export default function ScoreBadge({ score, label }: ScoreBadgeProps) {
  return (
    <Chip
      label={label ? `${label}: ${score}` : score}
      color={getScoreColor(score)}
      size="small"
      sx={{ fontWeight: 600 }}
    />
  )
}
