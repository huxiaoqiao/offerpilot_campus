import { Box, Typography } from '@mui/material'

interface ScoreGaugeProps {
  score: number
  size?: number
  label?: string
}

function getScoreColor(score: number): string {
  if (score >= 80) return '#10B981'
  if (score >= 60) return '#3B82F6'
  if (score >= 40) return '#F59E0B'
  return '#EF4444'
}

export default function ScoreGauge({ score, size = 120, label }: ScoreGaugeProps) {
  const strokeWidth = size * 0.08
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const progress = Math.min(Math.max(score, 0), 100) / 100
  const offset = circumference - progress * circumference
  const color = getScoreColor(score)

  return (
    <Box sx={{ display: 'inline-flex', flexDirection: 'column', alignItems: 'center', gap: 0.5 }}>
      <svg width={size} height={size}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
        <text
          x="50%"
          y="50%"
          textAnchor="middle"
          dominantBaseline="central"
          fontSize={size * 0.3}
          fontWeight={700}
          fill={color}
        >
          {Math.round(score)}
        </text>
      </svg>
      {label && (
        <Typography variant="caption" color="text.secondary" sx={{ mt: -0.5 }}>
          {label}
        </Typography>
      )}
    </Box>
  )
}
