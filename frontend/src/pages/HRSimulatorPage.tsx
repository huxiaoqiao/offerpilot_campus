import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box, Typography, Button, Select, MenuItem, FormControl, InputLabel,
  Card, CardContent, Stack, Grid, Chip, LinearProgress, Paper, Avatar,
} from '@mui/material'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import CancelIcon from '@mui/icons-material/Cancel'
import PersonIcon from '@mui/icons-material/Person'
import { useHRStore } from '../store/hrStore'
import { useJobsStore } from '../store/jobsStore'
import ErrorAlert from '../components/common/ErrorAlert'
import LoadingOverlay from '../components/common/LoadingOverlay'
import ScoreGauge from '../components/common/ScoreGauge'
import EmptyState from '../components/common/EmptyState'

function PriorityChip({ priority }: { priority: string }) {
  const colorMap: Record<string, 'error' | 'warning' | 'info'> = {
    '高': 'error', '中': 'warning', '低': 'info',
  }
  return <Chip label={`优先级: ${priority}`} size="small" color={colorMap[priority] || 'default'} />
}

export default function HRSimulatorPage() {
  const { jobId: urlJobId } = useParams<{ jobId: string }>()
  const navigate = useNavigate()
  const { simulation, loading, error, runSimulation, fetchSimulation, clearError } = useHRStore()
  const { jobs, fetchJobs } = useJobsStore()
  const [selectedJobId, setSelectedJobId] = useState<string>(urlJobId || '')

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  useEffect(() => {
    if (urlJobId) {
      setSelectedJobId(urlJobId)
      fetchSimulation(urlJobId)
    }
  }, [urlJobId, fetchSimulation])

  const handleRun = async () => {
    if (!selectedJobId) return
    await runSimulation(selectedJobId)
  }

  const handleJobChange = (jobId: string) => {
    setSelectedJobId(jobId)
    navigate(`/hr/${jobId}`)
    fetchSimulation(jobId)
  }

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>HR模拟器</Typography>
      <ErrorAlert error={error} onClose={clearError} />

      <Stack direction="row" spacing={2} sx={{ mb: 3 }} alignItems="center">
        <FormControl size="small" sx={{ minWidth: 300 }}>
          <InputLabel>选择岗位</InputLabel>
          <Select
            value={selectedJobId}
            label="选择岗位"
            onChange={(e) => handleJobChange(e.target.value)}
          >
            {jobs.map((job) => (
              <MenuItem key={job.id} value={job.id}>
                {job.position_title} - {job.company_name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <Button variant="contained" onClick={handleRun} disabled={!selectedJobId || loading}>
          运行HR模拟
        </Button>
      </Stack>

      <Box sx={{ position: 'relative', minHeight: 200 }}>
        <LoadingOverlay loading={loading} message="正在模拟HR筛选..." />

        {!simulation && !loading && (
          <EmptyState
            title="暂无HR模拟结果"
            description={'选择一个岗位后点击「运行HR模拟」开始分析'}
          />
        )}

        {simulation && (
          <>
            {/* Pass Probability */}
            <Card sx={{ mb: 3 }}>
              <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <ScoreGauge
                  score={simulation.screening_result.pass_probability}
                  size={140}
                  label="通过概率"
                />
                <Box sx={{ flex: 1 }}>
                  <Typography variant="h4" fontWeight={700}>
                    {Math.round(simulation.screening_result.pass_probability)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    简历初筛通过概率
                  </Typography>
                </Box>
              </CardContent>
            </Card>

            {/* Pass / Fail Reasons */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2, height: '100%', borderTop: '3px solid #10B981' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                    <CheckCircleIcon sx={{ color: '#10B981' }} />
                    <Typography variant="subtitle1" fontWeight={600}>通过理由</Typography>
                  </Box>
                  <Stack spacing={1}>
                    {simulation.screening_result.pass_reasons.map((reason, i) => (
                      <Box key={i} sx={{ display: 'flex', gap: 1 }}>
                        <CheckCircleIcon sx={{ color: '#10B981', fontSize: 16, mt: 0.3 }} />
                        <Typography variant="body2">{reason}</Typography>
                      </Box>
                    ))}
                    {simulation.screening_result.pass_reasons.length === 0 && (
                      <Typography variant="body2" color="text.disabled">暂无</Typography>
                    )}
                  </Stack>
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2, height: '100%', borderTop: '3px solid #EF4444' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                    <CancelIcon sx={{ color: '#EF4444' }} />
                    <Typography variant="subtitle1" fontWeight={600}>拒绝理由</Typography>
                  </Box>
                  <Stack spacing={1}>
                    {simulation.screening_result.fail_reasons.map((reason, i) => (
                      <Box key={i} sx={{ display: 'flex', gap: 1 }}>
                        <CancelIcon sx={{ color: '#EF4444', fontSize: 16, mt: 0.3 }} />
                        <Typography variant="body2">{reason}</Typography>
                      </Box>
                    ))}
                    {simulation.screening_result.fail_reasons.length === 0 && (
                      <Typography variant="body2" color="text.disabled">暂无</Typography>
                    )}
                  </Stack>
                </Paper>
              </Grid>
            </Grid>

            {/* ATS Check */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>ATS检查</Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={4}>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                      关键词匹配率
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={simulation.ats_check.keyword_match_rate * 100}
                        sx={{ flex: 1, height: 8, borderRadius: 4 }}
                        color={simulation.ats_check.keyword_match_rate >= 0.7 ? 'success' : simulation.ats_check.keyword_match_rate >= 0.4 ? 'warning' : 'error'}
                      />
                      <Typography variant="body2" fontWeight={600}>
                        {Math.round(simulation.ats_check.keyword_match_rate * 100)}%
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                      格式合规
                    </Typography>
                    <Chip
                      label={simulation.ats_check.format_compliance ? '合规' : '不合规'}
                      color={simulation.ats_check.format_compliance ? 'success' : 'error'}
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                      可读性分数
                    </Typography>
                    <Typography variant="h6" fontWeight={700}>
                      {simulation.ats_check.readability_score}
                    </Typography>
                  </Grid>
                </Grid>
                {simulation.ats_check.issues.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" sx={{ mb: 0.5 }}>问题列表</Typography>
                    {simulation.ats_check.issues.map((issue, i) => (
                      <Typography key={i} variant="body2" color="error.main">
                        - {issue}
                      </Typography>
                    ))}
                  </Box>
                )}
              </CardContent>
            </Card>

            {/* HR Feedback */}
            <Card>
              <CardContent>
                <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>HR反馈</Typography>
                <Stack spacing={1.5}>
                  {simulation.hr_feedback.map((fb, i) => (
                    <Box key={i} sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
                      <Avatar sx={{ width: 36, height: 36, bgcolor: 'primary.main' }}>
                        <PersonIcon sx={{ fontSize: 20 }} />
                      </Avatar>
                      <Paper variant="outlined" sx={{ p: 1.5, flex: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                          <Chip label={fb.category} size="small" variant="outlined" />
                          <PriorityChip priority={fb.priority} />
                        </Box>
                        <Typography variant="body2">{fb.feedback}</Typography>
                      </Paper>
                    </Box>
                  ))}
                  {simulation.hr_feedback.length === 0 && (
                    <Typography variant="body2" color="text.disabled">暂无反馈</Typography>
                  )}
                </Stack>
              </CardContent>
            </Card>
          </>
        )}
      </Box>
    </Box>
  )
}
