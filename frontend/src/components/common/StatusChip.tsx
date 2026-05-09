import { Chip } from '@mui/material'

const STATUS_COLOR_MAP: Record<string, { bg: string; color: string }> = {
  '待评估': { bg: '#9ca3af', color: '#fff' },
  '已评估': { bg: '#3B82F6', color: '#fff' },
  '准备中': { bg: '#8B5CF6', color: '#fff' },
  '已投递': { bg: '#F59E0B', color: '#fff' },
  '面试中': { bg: '#06B6D4', color: '#fff' },
  '已offer': { bg: '#10B981', color: '#fff' },
  '已拒绝': { bg: '#EF4444', color: '#fff' },
  '放弃': { bg: '#6b7280', color: '#fff' },
}

interface StatusChipProps {
  status: string
}

export default function StatusChip({ status }: StatusChipProps) {
  const style = STATUS_COLOR_MAP[status] || { bg: '#9ca3af', color: '#fff' }
  return (
    <Chip
      label={status}
      size="small"
      sx={{
        bgcolor: style.bg,
        color: style.color,
        fontWeight: 600,
        fontSize: '0.75rem',
      }}
    />
  )
}
