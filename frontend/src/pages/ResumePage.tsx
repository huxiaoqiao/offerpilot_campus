import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box, Typography, Button, Select, MenuItem, FormControl, InputLabel,
  Card, CardContent, Stack, Grid, Chip, Collapse, Divider, Dialog,
  DialogTitle, DialogContent, DialogActions, IconButton, Paper,
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import VisibilityIcon from '@mui/icons-material/Visibility'
import CloseIcon from '@mui/icons-material/Close'
import { useResumeStore } from '../store/resumeStore'
import { useJobsStore } from '../store/jobsStore'
import ErrorAlert from '../components/common/ErrorAlert'
import LoadingOverlay from '../components/common/LoadingOverlay'
import EmptyState from '../components/common/EmptyState'

function SkillChangeChip({ action }: { action: string }) {
  const colorMap: Record<string, 'success' | 'warning' | 'error' | 'default'> = {
    '置顶': 'success', '新增': 'success', '移除': 'error', '重排序': 'warning',
  }
  return <Chip label={action} size="small" color={colorMap[action] || 'default'} />
}

export default function ResumePage() {
  const { jobId: urlJobId } = useParams<{ jobId: string }>()
  const navigate = useNavigate()
  const { currentResume, htmlPreview, loading, error, generate, fetchResume, fetchHtmlPreview, clearError } = useResumeStore()
  const { jobs, fetchJobs } = useJobsStore()
  const [selectedJobId, setSelectedJobId] = useState<string>(urlJobId || '')
  const [previewOpen, setPreviewOpen] = useState(false)
  const [expandedExp, setExpandedExp] = useState<number | null>(null)

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  useEffect(() => {
    if (urlJobId) {
      setSelectedJobId(urlJobId)
      fetchResume(urlJobId)
    }
  }, [urlJobId, fetchResume])

  const handleGenerate = async () => {
    if (!selectedJobId) return
    await generate(selectedJobId)
  }

  const handlePreview = async () => {
    if (!selectedJobId) return
    await fetchHtmlPreview(selectedJobId)
    setPreviewOpen(true)
  }

  const handleJobChange = (jobId: string) => {
    setSelectedJobId(jobId)
    navigate(`/resume/${jobId}`)
    fetchResume(jobId)
  }

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>简历改写</Typography>
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
        <Button variant="contained" onClick={handleGenerate} disabled={!selectedJobId || loading}>
          生成定制简历
        </Button>
        {currentResume && (
          <Button variant="outlined" startIcon={<VisibilityIcon />} onClick={handlePreview}>
            预览完整简历
          </Button>
        )}
      </Stack>

      <Box sx={{ position: 'relative', minHeight: 200 }}>
        <LoadingOverlay loading={loading} message="正在生成定制简历..." />

        {!currentResume && !loading && (
          <EmptyState
            title="暂无定制简历"
            description={'选择一个岗位后点击「生成定制简历」'}
          />
        )}

        {currentResume && (
          <>
            {/* Summary Section */}
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>个人总结</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="caption" color="text.secondary">来源: {currentResume.sections.summary.source}</Typography>
                    <Paper variant="outlined" sx={{ p: 1.5, mt: 0.5, bgcolor: '#f9fafb' }}>
                      <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                        {currentResume.sections.summary.content}
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="caption" color="success.main">改写后</Typography>
                    <Paper variant="outlined" sx={{ p: 1.5, mt: 0.5, bgcolor: '#f0fdf4' }}>
                      <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                        {currentResume.sections.summary.content}
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Skills Section */}
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>技能</Typography>
                <Stack direction="row" spacing={0.5} sx={{ flexWrap: 'wrap', gap: 0.5, mb: 1.5 }}>
                  {currentResume.sections.skills.content.map((skill) => (
                    <Chip key={skill} label={skill} size="small" />
                  ))}
                </Stack>
                {currentResume.sections.skills.changes.length > 0 && (
                  <>
                    <Typography variant="subtitle2" sx={{ mb: 0.5 }}>变更详情</Typography>
                    {currentResume.sections.skills.changes.map((change, i) => (
                      <Box key={i} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                        <SkillChangeChip action={change.action} />
                        <Typography variant="body2" fontWeight={600}>{change.skill}</Typography>
                        <Typography variant="body2" color="text.secondary">- {change.reason}</Typography>
                      </Box>
                    ))}
                  </>
                )}
              </CardContent>
            </Card>

            {/* Experiences Section */}
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1.5 }}>经历改写</Typography>
                {currentResume.sections.experiences.map((exp, i) => (
                  <Card key={i} variant="outlined" sx={{ mb: 1.5, cursor: 'pointer' }}
                    onClick={() => setExpandedExp(expandedExp === i ? null : i)}
                  >
                    <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="body2" fontWeight={600}>
                          经历 {i + 1}
                        </Typography>
                        {expandedExp === i ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
                      </Box>
                      <Collapse in={expandedExp === i}>
                        <Grid container spacing={2} sx={{ mt: 1 }}>
                          <Grid item xs={12} md={6}>
                            <Typography variant="caption" color="text.secondary">原文</Typography>
                            <Paper variant="outlined" sx={{ p: 1.5, mt: 0.5, bgcolor: '#f9fafb' }}>
                              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                                {exp.original}
                              </Typography>
                            </Paper>
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <Typography variant="caption" color="success.main">改写后</Typography>
                            <Paper variant="outlined" sx={{ p: 1.5, mt: 0.5, bgcolor: '#f0fdf4' }}>
                              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                                {exp.rewritten}
                              </Typography>
                            </Paper>
                          </Grid>
                        </Grid>
                        {exp.changes.length > 0 && (
                          <Box sx={{ mt: 1 }}>
                            <Typography variant="caption" color="text.secondary">变更点:</Typography>
                            {exp.changes.map((c, ci) => (
                              <Typography key={ci} variant="body2" color="text.secondary">- {c}</Typography>
                            ))}
                          </Box>
                        )}
                      </Collapse>
                    </CardContent>
                  </Card>
                ))}
              </CardContent>
            </Card>

            {/* Job Intention */}
            <Card>
              <CardContent>
                <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>求职意向</Typography>
                <Typography variant="caption" color="text.secondary">
                  来源: {currentResume.sections.job_intention.source}
                </Typography>
                <Paper variant="outlined" sx={{ p: 1.5, mt: 0.5, bgcolor: '#f0fdf4' }}>
                  <Typography variant="body2">{currentResume.sections.job_intention.content}</Typography>
                </Paper>
              </CardContent>
            </Card>
          </>
        )}
      </Box>

      {/* HTML Preview Dialog */}
      <Dialog open={previewOpen} onClose={() => setPreviewOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          简历预览
          <IconButton onClick={() => setPreviewOpen(false)}><CloseIcon /></IconButton>
        </DialogTitle>
        <DialogContent dividers>
          <Box
            sx={{ p: 2 }}
            dangerouslySetInnerHTML={{ __html: htmlPreview }}
          />
        </DialogContent>
      </Dialog>
    </Box>
  )
}
