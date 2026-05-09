import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box, Typography, Card, CardContent, Button, Select, MenuItem,
  FormControl, InputLabel, Stack, Chip, Collapse, IconButton,
  Divider, Grid, Paper,
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import EditIcon from '@mui/icons-material/Edit'
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts'
import { useMatchStore } from '../store/matchStore'
import { useJobsStore } from '../store/jobsStore'
import ErrorAlert from '../components/common/ErrorAlert'
import LoadingOverlay from '../components/common/LoadingOverlay'
import ScoreGauge from '../components/common/ScoreGauge'
import ScoreBadge from '../components/common/ScoreBadge'
import EmptyState from '../components/common/EmptyState'

const DIMENSION_LABELS: Record<string, string> = {
  skill_match: '技能匹配',
  experience_match: '经历匹配',
  education_match: '学历匹配',
  project_match: '项目匹配',
  culture_match: '文化匹配',
  technical_depth: '技术深度',
  soft_skill: '软技能',
  industry_fit: '行业适配',
}

function StrengthChip({ strength }: { strength: string }) {
  const colorMap: Record<string, 'success' | 'warning' | 'error'> = {
    '强': 'success', '中': 'warning', '弱': 'error',
  }
  return <Chip label={strength} size="small" color={colorMap[strength] || 'default'} />
}

function SeverityChip({ severity }: { severity: string }) {
  const colorMap: Record<string, 'error' | 'warning' | 'info'> = {
    '高': 'error', '中': 'warning', '低': 'info',
  }
  return <Chip label={severity} size="small" color={colorMap[severity] || 'default'} variant="outlined" />
}

function RiskLevelChip({ level }: { level: string }) {
  const colorMap: Record<string, 'error' | 'warning' | 'info'> = {
    '高': 'error', '中': 'warning', '低': 'info',
  }
  return <Chip label={level} size="small" color={colorMap[level] || 'default'} variant="outlined" />
}

export default function MatchPage() {
  const { jobId: urlJobId } = useParams<{ jobId: string }>()
  const navigate = useNavigate()
  const { currentResult, loading, error, runMatch, fetchMatch, clearError } = useMatchStore()
  const { jobs, fetchJobs } = useJobsStore()
  const [selectedJobId, setSelectedJobId] = useState<string>(urlJobId || '')
  const [expandedEvidence, setExpandedEvidence] = useState<number | null>(null)

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  useEffect(() => {
    if (urlJobId) {
      setSelectedJobId(urlJobId)
      fetchMatch(urlJobId)
    }
  }, [urlJobId, fetchMatch])

  const handleRunMatch = async () => {
    if (!selectedJobId) return
    await runMatch(selectedJobId)
  }

  const handleJobChange = (jobId: string) => {
    setSelectedJobId(jobId)
    navigate(`/match/${jobId}`)
    fetchMatch(jobId)
  }

  const radarData = currentResult
    ? Object.entries(currentResult.dimension_scores).map(([key, val]) => ({
        dimension: DIMENSION_LABELS[key] || key,
        score: val.score,
        fullMark: 100,
      }))
    : []

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>匹配解释</Typography>
      <ErrorAlert error={error} onClose={clearError} />

      {/* Job Selector */}
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
        <Button
          variant="contained"
          onClick={handleRunMatch}
          disabled={!selectedJobId || loading}
        >
          运行匹配
        </Button>
      </Stack>

      <Box sx={{ position: 'relative', minHeight: 200 }}>
        <LoadingOverlay loading={loading} message="正在分析匹配度..." />

        {!currentResult && !loading && (
          <EmptyState
            title="暂无匹配结果"
            description={'选择一个岗位后点击「运行匹配」开始分析'}
          />
        )}

        {currentResult && (
          <>
            {/* Total Score Card */}
            <Card sx={{ mb: 3 }}>
              <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <ScoreGauge score={currentResult.total_score} size={140} label="总分" />
                <Box sx={{ flex: 1 }}>
                  <Typography variant="h4" fontWeight={700}>
                    {currentResult.total_score}
                  </Typography>
                  <Chip
                    label={currentResult.opportunity_level}
                    color="primary"
                    sx={{ mt: 0.5, fontWeight: 600 }}
                  />
                  {currentResult.improvement_actions.length > 0 && (
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="subtitle2" color="text.secondary">改进建议:</Typography>
                      {currentResult.improvement_actions.slice(0, 3).map((a, i) => (
                        <Typography key={i} variant="body2" color="text.secondary">
                          - {a}
                        </Typography>
                      ))}
                    </Box>
                  )}
                </Box>
              </CardContent>
            </Card>

            {/* Radar Chart */}
            {radarData.length > 0 && (
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>分维度评分</Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <RadarChart data={radarData}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 12 }} />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 10 }} />
                      <Radar
                        name="得分"
                        dataKey="score"
                        stroke="#3B82F6"
                        fill="#3B82F6"
                        fillOpacity={0.3}
                      />
                      <Tooltip />
                    </RadarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            )}

            {/* Three Columns: Evidence | Gaps | Risks */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
              {/* Evidence Column */}
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2, height: '100%' }}>
                  <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1.5 }}>
                    证据命中 ({currentResult.matched_evidence.length})
                  </Typography>
                  <Stack spacing={1.5}>
                    {currentResult.matched_evidence.map((e, i) => (
                      <Card key={i} variant="outlined" sx={{ cursor: 'pointer' }}
                        onClick={() => setExpandedEvidence(expandedEvidence === i ? null : i)}
                      >
                        <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="body2" fontWeight={600} sx={{ flex: 1 }}>
                              {e.jd_requirement}
                            </Typography>
                            <StrengthChip strength={e.strength} />
                          </Box>
                          <Collapse in={expandedEvidence === i}>
                            <Box sx={{ mt: 1 }}>
                              <Typography variant="body2" color="text.secondary">
                                简历证据: {e.resume_evidence}
                              </Typography>
                              <Typography variant="caption" color="text.disabled">
                                来源: {e.evidence_source}
                              </Typography>
                            </Box>
                          </Collapse>
                        </CardContent>
                      </Card>
                    ))}
                    {currentResult.matched_evidence.length === 0 && (
                      <Typography variant="body2" color="text.disabled">暂无匹配证据</Typography>
                    )}
                  </Stack>
                </Paper>
              </Grid>

              {/* Gaps Column */}
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2, height: '100%' }}>
                  <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1.5 }}>
                    缺口分析 ({currentResult.gaps.length})
                  </Typography>
                  <Stack spacing={1.5}>
                    {currentResult.gaps.map((g, i) => (
                      <Card key={i} variant="outlined">
                        <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                            <Typography variant="body2" fontWeight={600}>{g.jd_requirement}</Typography>
                            <SeverityChip severity={g.severity} />
                          </Box>
                          <Typography variant="body2" color="text.secondary">{g.suggestion}</Typography>
                          <Button
                            size="small"
                            startIcon={<EditIcon />}
                            sx={{ mt: 0.5, textTransform: 'none' }}
                            onClick={() => navigate('/profile')}
                          >
                            去改简历
                          </Button>
                        </CardContent>
                      </Card>
                    ))}
                    {currentResult.gaps.length === 0 && (
                      <Typography variant="body2" color="text.disabled">暂无明显缺口</Typography>
                    )}
                  </Stack>
                </Paper>
              </Grid>

              {/* Risks Column */}
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2, height: '100%' }}>
                  <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1.5 }}>
                    风险提示 ({currentResult.risks.length})
                  </Typography>
                  <Stack spacing={1.5}>
                    {currentResult.risks.map((r, i) => (
                      <Card key={i} variant="outlined">
                        <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                            <Typography variant="body2" fontWeight={600}>{r.risk}</Typography>
                            <RiskLevelChip level={r.level} />
                          </Box>
                          <Typography variant="body2" color="text.secondary">{r.mitigation}</Typography>
                        </CardContent>
                      </Card>
                    ))}
                    {currentResult.risks.length === 0 && (
                      <Typography variant="body2" color="text.disabled">暂无风险</Typography>
                    )}
                  </Stack>
                </Paper>
              </Grid>
            </Grid>

            {/* Dimension Details */}
            <Card>
              <CardContent>
                <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1.5 }}>维度详情</Typography>
                <Stack spacing={1}>
                  {Object.entries(currentResult.dimension_scores).map(([key, val]) => (
                    <Box key={key} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Typography variant="body2" sx={{ minWidth: 100, fontWeight: 600 }}>
                        {DIMENSION_LABELS[key] || key}
                      </Typography>
                      <Box sx={{ flex: 1 }}>
                        <Box sx={{ height: 8, bgcolor: '#e5e7eb', borderRadius: 4, overflow: 'hidden' }}>
                          <Box sx={{
                            height: '100%',
                            width: `${val.score}%`,
                            bgcolor: val.score >= 80 ? '#10B981' : val.score >= 60 ? '#3B82F6' : val.score >= 40 ? '#F59E0B' : '#EF4444',
                            borderRadius: 4,
                          }} />
                        </Box>
                      </Box>
                      <ScoreBadge score={val.score} />
                      <Typography variant="caption" color="text.secondary" sx={{ flex: 1 }}>
                        {val.detail}
                      </Typography>
                    </Box>
                  ))}
                </Stack>
              </CardContent>
            </Card>
          </>
        )}
      </Box>
    </Box>
  )
}
