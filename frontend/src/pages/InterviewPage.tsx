import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box, Typography, Button, Select, MenuItem, FormControl, InputLabel,
  Card, CardContent, Stack, Grid, Chip, Collapse, List, ListItemButton,
  ListItemText, ListItemIcon, Tabs, Tab, Paper, Divider,
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer'
import PsychologyIcon from '@mui/icons-material/Psychology'
import CodeIcon from '@mui/icons-material/Code'
import TheaterComedyIcon from '@mui/icons-material/TheaterComedy'
import HelpOutlineIcon from '@mui/icons-material/HelpOutline'
import PersonIcon from '@mui/icons-material/Person'
import WarningAmberIcon from '@mui/icons-material/WarningAmber'
import { useInterviewStore } from '../store/interviewStore'
import { useJobsStore } from '../store/jobsStore'
import ErrorAlert from '../components/common/ErrorAlert'
import LoadingOverlay from '../components/common/LoadingOverlay'
import EmptyState from '../components/common/EmptyState'
import type { InterviewQuestion, STARStory } from '../types/interview'

const CATEGORY_CONFIG: Record<string, { color: string; icon: React.ReactNode }> = {
  '自我介绍': { color: '#3B82F6', icon: <PersonIcon fontSize="small" /> },
  '行为面试': { color: '#10B981', icon: <PsychologyIcon fontSize="small" /> },
  '技术问题': { color: '#F59E0B', icon: <CodeIcon fontSize="small" /> },
  '情景模拟': { color: '#8B5CF6', icon: <TheaterComedyIcon fontSize="small" /> },
  '反问环节': { color: '#6b7280', icon: <HelpOutlineIcon fontSize="small" /> },
}

function CategoryChip({ category }: { category: string }) {
  const config = CATEGORY_CONFIG[category] || { color: '#6b7280', icon: null }
  return (
    <Chip
      label={category}
      size="small"
      icon={config.icon as any}
      sx={{ bgcolor: config.color, color: '#fff', '& .MuiChip-icon': { color: '#fff' } }}
    />
  )
}

export default function InterviewPage() {
  const { jobId: urlJobId } = useParams<{ jobId: string }>()
  const navigate = useNavigate()
  const { data, loading, error, selectedQuestionId, generate, fetchData, selectQuestion, clearError } = useInterviewStore()
  const { jobs, fetchJobs } = useJobsStore()
  const [selectedJobId, setSelectedJobId] = useState<string>(urlJobId || '')
  const [tab, setTab] = useState(0)
  const [expandedStory, setExpandedStory] = useState<number | null>(null)
  const [showFramework, setShowFramework] = useState(false)

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  useEffect(() => {
    if (urlJobId) {
      setSelectedJobId(urlJobId)
      fetchData(urlJobId)
    }
  }, [urlJobId, fetchData])

  const handleGenerate = async () => {
    if (!selectedJobId) return
    await generate(selectedJobId)
  }

  const handleJobChange = (jobId: string) => {
    setSelectedJobId(jobId)
    navigate(`/interview/${jobId}`)
    fetchData(jobId)
  }

  const selectedQuestion = data?.questions.find((q) => q.id === selectedQuestionId) || null

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>面试训练</Typography>
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
        <Button variant="contained" onClick={handleGenerate} disabled={!selectedJobId || loading}>
          生成面试题
        </Button>
      </Stack>

      <Box sx={{ position: 'relative', minHeight: 200 }}>
        <LoadingOverlay loading={loading} message="正在生成面试题..." />

        {!data && !loading && (
          <EmptyState
            title="暂无面试题"
            description={'选择一个岗位后点击「生成面试题」'}
          />
        )}

        {data && (
          <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
            <Tab label={`面试题 (${data.questions.length})`} />
            <Tab label={`STAR故事 (${data.star_stories.length})`} />
            <Tab label={`风险追问 (${data.risk_followups.length})`} />
          </Tabs>
        )}

        {/* Tab 0: Questions */}
        {data && tab === 0 && (
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Paper sx={{ maxHeight: 600, overflow: 'auto' }}>
                <List disablePadding>
                  {data.questions.map((q) => {
                    const config = CATEGORY_CONFIG[q.category] || { color: '#6b7280' }
                    return (
                      <ListItemButton
                        key={q.id}
                        selected={selectedQuestionId === q.id}
                        onClick={() => { selectQuestion(q.id); setShowFramework(false) }}
                        sx={{
                          borderLeft: `3px solid ${config.color}`,
                          '&.Mui-selected': { bgcolor: 'action.selected' },
                        }}
                      >
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          <CategoryChip category={q.category} />
                        </ListItemIcon>
                        <ListItemText
                          primary={q.question}
                          primaryTypographyProps={{ variant: 'body2', noWrap: true }}
                        />
                      </ListItemButton>
                    )
                  })}
                </List>
              </Paper>
            </Grid>

            <Grid item xs={12} md={8}>
              {selectedQuestion ? (
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box>
                        <CategoryChip category={selectedQuestion.category} />
                        <Typography variant="h6" sx={{ mt: 1 }}>
                          {selectedQuestion.question}
                        </Typography>
                      </Box>
                    </Box>

                    <Divider sx={{ mb: 2 }} />

                    <Box sx={{ mb: 2 }}>
                      <Button
                        size="small"
                        onClick={() => setShowFramework(!showFramework)}
                        endIcon={showFramework ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                      >
                        参考答案框架
                      </Button>
                      <Collapse in={showFramework}>
                        <Paper variant="outlined" sx={{ p: 2, mt: 1, bgcolor: '#f9fafb' }}>
                          <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                            {selectedQuestion.reference_answer_framework}
                          </Typography>
                        </Paper>
                      </Collapse>
                    </Box>

                    {selectedQuestion.related_resume_item && (
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="subtitle2" color="text.secondary">关联简历项</Typography>
                        <Paper variant="outlined" sx={{ p: 1.5, mt: 0.5 }}>
                          <Typography variant="body2">{selectedQuestion.related_resume_item}</Typography>
                        </Paper>
                      </Box>
                    )}

                    {selectedQuestion.related_risk && (
                      <Box sx={{ mb: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                          <WarningAmberIcon sx={{ color: 'warning.main', fontSize: 16 }} />
                          <Typography variant="subtitle2" color="warning.main">关联风险</Typography>
                        </Box>
                        <Paper variant="outlined" sx={{ p: 1.5, bgcolor: '#fffbeb' }}>
                          <Typography variant="body2">{selectedQuestion.related_risk}</Typography>
                        </Paper>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              ) : (
                <EmptyState title="选择一道题目查看详情" />
              )}
            </Grid>
          </Grid>
        )}

        {/* Tab 1: STAR Stories */}
        {data && tab === 1 && (
          <Stack spacing={2}>
            {data.star_stories.map((story, i) => (
              <Card key={i} variant="outlined" sx={{ cursor: 'pointer' }}
                onClick={() => setExpandedStory(expandedStory === i ? null : i)}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="subtitle1" fontWeight={600}>{story.title}</Typography>
                    {expandedStory === i ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                  </Box>
                  <Collapse in={expandedStory === i}>
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                      {[
                        { label: 'Situation (情境)', value: story.situation },
                        { label: 'Task (任务)', value: story.task },
                        { label: 'Action (行动)', value: story.action },
                        { label: 'Result (结果)', value: story.result },
                      ].map(({ label, value }) => (
                        <Grid item xs={12} sm={6} key={label}>
                          <Typography variant="caption" fontWeight={600} color="primary.main">{label}</Typography>
                          <Paper variant="outlined" sx={{ p: 1.5, mt: 0.5 }}>
                            <Typography variant="body2">{value}</Typography>
                          </Paper>
                        </Grid>
                      ))}
                    </Grid>
                    {story.applicable_questions.length > 0 && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="caption" color="text.secondary">适用问题:</Typography>
                        <Stack direction="row" spacing={0.5} sx={{ flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                          {story.applicable_questions.map((q, qi) => (
                            <Chip key={qi} label={q} size="small" variant="outlined" />
                          ))}
                        </Stack>
                      </Box>
                    )}
                  </Collapse>
                </CardContent>
              </Card>
            ))}
            {data.star_stories.length === 0 && (
              <EmptyState title="暂无STAR故事" />
            )}
          </Stack>
        )}

        {/* Tab 2: Risk Followups */}
        {data && tab === 2 && (
          <Stack spacing={2}>
            {data.risk_followups.map((rf, i) => (
              <Card key={i} variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <WarningAmberIcon sx={{ color: 'warning.main', fontSize: 20 }} />
                    <Typography variant="subtitle1" fontWeight={600}>{rf.risk}</Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    可能的追问: {rf.possible_question}
                  </Typography>
                  <Paper variant="outlined" sx={{ p: 1.5, bgcolor: '#f0fdf4' }}>
                    <Typography variant="caption" color="success.main" fontWeight={600}>建议回答</Typography>
                    <Typography variant="body2" sx={{ mt: 0.5 }}>{rf.suggested_answer}</Typography>
                  </Paper>
                </CardContent>
              </Card>
            ))}
            {data.risk_followups.length === 0 && (
              <EmptyState title="暂无风险追问" />
            )}
          </Stack>
        )}
      </Box>
    </Box>
  )
}
