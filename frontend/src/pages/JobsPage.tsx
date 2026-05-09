import { useState, useEffect, useCallback } from 'react'
import {
  Box, Typography, TextField, Button, Card, CardContent, Stack, Dialog,
  DialogTitle, DialogContent, DialogActions, Chip, IconButton, Tooltip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, TablePagination,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import DeleteIcon from '@mui/icons-material/Delete'
import RefreshIcon from '@mui/icons-material/Refresh'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import { useJobsStore } from '../store/jobsStore'
import ErrorAlert from '../components/common/ErrorAlert'
import LoadingOverlay from '../components/common/LoadingOverlay'
import EmptyState from '../components/common/EmptyState'
import ScoreBadge from '../components/common/ScoreBadge'
import type { JobPost } from '../types/job'

function QualityScoreCell({ score }: { score: number }) {
  const color = score >= 70 ? '#10B981' : score >= 40 ? '#F59E0B' : '#EF4444'
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
      <Box
        sx={{
          width: 8,
          height: 8,
          borderRadius: '50%',
          bgcolor: color,
        }}
      />
      <Typography variant="body2" fontWeight={600}>{score}</Typography>
    </Box>
  )
}

export default function JobsPage() {
  const {
    jobs, total, loading, error, currentPage, pageSize,
    fetchJobs, createJob, batchCreate, importCsv, deleteJob, reparse,
    setPage, clearError,
  } = useJobsStore()

  const [jdText, setJdText] = useState('')
  const [batchOpen, setBatchOpen] = useState(false)
  const [batchText, setBatchText] = useState('')
  const [csvOpen, setCsvOpen] = useState(false)
  const [expandedRow, setExpandedRow] = useState<string | null>(null)

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  const handleParseSingle = async () => {
    if (!jdText.trim()) return
    await createJob({ jd_text: jdText.trim() })
    setJdText('')
  }

  const handleBatchImport = async () => {
    const lines = batchText.split('\n').filter((l) => l.trim())
    if (!lines.length) return
    const jobsData = lines.map((line) => ({ jd_text: line.trim() }))
    await batchCreate(jobsData)
    setBatchText('')
    setBatchOpen(false)
  }

  const handleCsvUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    await importCsv(file)
    setCsvOpen(false)
  }

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage)
  }

  const formatSalary = (min: number | null, max: number | null) => {
    if (min === null && max === null) return '-'
    if (min !== null && max !== null) return `${min}K-${max}K`
    if (min !== null) return `${min}K+`
    return `≤${max}K`
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">岗位雷达</Typography>
        <Stack direction="row" spacing={1}>
          <Button variant="outlined" startIcon={<UploadFileIcon />} onClick={() => setBatchOpen(true)}>
            批量导入
          </Button>
          <Button variant="outlined" startIcon={<UploadFileIcon />} onClick={() => setCsvOpen(true)}>
            CSV上传
          </Button>
        </Stack>
      </Box>

      <ErrorAlert error={error} onClose={clearError} />

      {/* JD Input */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>粘贴JD文本解析</Typography>
          <TextField
            multiline
            rows={4}
            fullWidth
            placeholder="粘贴岗位描述文本..."
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            sx={{ mb: 1.5 }}
          />
          <Button
            variant="contained"
            onClick={handleParseSingle}
            disabled={!jdText.trim() || loading}
          >
            解析
          </Button>
        </CardContent>
      </Card>

      {/* Jobs Table */}
      <Box sx={{ position: 'relative' }}>
        <LoadingOverlay loading={loading} message="加载中..." />

        {jobs.length === 0 && !loading ? (
          <EmptyState
            title="暂无岗位数据"
            description="粘贴JD文本解析，或批量导入岗位信息"
          />
        ) : (
          <Paper>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>岗位名称</TableCell>
                    <TableCell>公司</TableCell>
                    <TableCell>城市</TableCell>
                    <TableCell>薪资范围</TableCell>
                    <TableCell>质量评分</TableCell>
                    <TableCell>状态</TableCell>
                    <TableCell align="right">操作</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {jobs.map((job) => (
                    <>
                      <TableRow
                        key={job.id}
                        hover
                        sx={{ cursor: 'pointer' }}
                        onClick={() => setExpandedRow(expandedRow === job.id ? null : job.id)}
                      >
                        <TableCell>
                          <Typography variant="body2" fontWeight={600}>
                            {job.position_title || '未命名岗位'}
                          </Typography>
                        </TableCell>
                        <TableCell>{job.company_name || '-'}</TableCell>
                        <TableCell>{job.city || '-'}</TableCell>
                        <TableCell>{formatSalary(job.salary_min, job.salary_max)}</TableCell>
                        <TableCell><QualityScoreCell score={job.quality_score} /></TableCell>
                        <TableCell>
                          <Chip label={job.status} size="small" variant="outlined" />
                        </TableCell>
                        <TableCell align="right">
                          <Tooltip title="重新解析">
                            <IconButton size="small" onClick={(e) => { e.stopPropagation(); reparse(job.id) }}>
                              <RefreshIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="删除">
                            <IconButton size="small" color="error" onClick={(e) => { e.stopPropagation(); deleteJob(job.id) }}>
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>

                      {/* Expanded Detail */}
                      {expandedRow === job.id && (
                        <TableRow key={`${job.id}-detail`}>
                          <TableCell colSpan={7}>
                            <Box sx={{ py: 2 }}>
                              <Typography variant="subtitle2" gutterBottom>岗位职责</Typography>
                              <Stack component="ul" sx={{ pl: 2, mb: 2 }}>
                                {job.responsibilities.map((r, i) => (
                                  <Typography key={i} component="li" variant="body2">{r}</Typography>
                                ))}
                              </Stack>

                              <Typography variant="subtitle2" gutterBottom>硬性要求</Typography>
                              <Stack component="ul" sx={{ pl: 2, mb: 2 }}>
                                {job.hard_requirements.map((r, i) => (
                                  <Typography key={i} component="li" variant="body2">{r}</Typography>
                                ))}
                              </Stack>

                              {job.soft_requirements.length > 0 && (
                                <>
                                  <Typography variant="subtitle2" gutterBottom>软性要求</Typography>
                                  <Stack component="ul" sx={{ pl: 2, mb: 2 }}>
                                    {job.soft_requirements.map((r, i) => (
                                      <Typography key={i} component="li" variant="body2">{r}</Typography>
                                    ))}
                                  </Stack>
                                </>
                              )}

                              <Typography variant="subtitle2" gutterBottom>关键词</Typography>
                              <Stack direction="row" spacing={0.5} sx={{ flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                                {job.keywords.map((k) => (
                                  <Chip key={k} label={k} size="small" variant="outlined" />
                                ))}
                              </Stack>

                              {job.risk_tags.length > 0 && (
                                <>
                                  <Typography variant="subtitle2" gutterBottom sx={{ mt: 1 }}>风险标签</Typography>
                                  <Stack direction="row" spacing={0.5} sx={{ flexWrap: 'wrap', gap: 0.5 }}>
                                    {job.risk_tags.map((t) => (
                                      <Chip key={t} label={t} size="small" color="error" variant="outlined" />
                                    ))}
                                  </Stack>
                                </>
                              )}
                            </Box>
                          </TableCell>
                        </TableRow>
                      )}
                    </>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              component="div"
              count={total}
              page={currentPage}
              onPageChange={handleChangePage}
              rowsPerPage={pageSize}
              rowsPerPageOptions={[pageSize]}
            />
          </Paper>
        )}
      </Box>

      {/* Batch Import Dialog */}
      <Dialog open={batchOpen} onClose={() => setBatchOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>批量导入JD</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            每行一个岗位描述文本
          </Typography>
          <TextField
            multiline
            rows={10}
            fullWidth
            placeholder={"岗位描述1...\n岗位描述2...\n岗位描述3..."}
            value={batchText}
            onChange={(e) => setBatchText(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBatchOpen(false)}>取消</Button>
          <Button variant="contained" onClick={handleBatchImport} disabled={!batchText.trim() || loading}>
            导入
          </Button>
        </DialogActions>
      </Dialog>

      {/* CSV Upload Dialog */}
      <Dialog open={csvOpen} onClose={() => setCsvOpen(false)}>
        <DialogTitle>CSV文件导入</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            上传CSV文件，自动解析岗位信息
          </Typography>
          <input type="file" accept=".csv" onChange={handleCsvUpload} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCsvOpen(false)}>关闭</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
