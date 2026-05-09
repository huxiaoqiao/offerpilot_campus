import { useState, useEffect } from 'react'
import {
  Box, Typography, Card, CardContent, Stack, Grid, Chip, Button,
  Dialog, DialogTitle, DialogContent, DialogActions, Select, MenuItem,
  FormControl, InputLabel, TextField, Paper, IconButton, Divider,
  Tooltip,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import DeleteIcon from '@mui/icons-material/Delete'
import CloseIcon from '@mui/icons-material/Close'
import { PieChart, Pie, Cell, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Tooltip as ReTooltip } from 'recharts'
import { useDashboardStore } from '../store/dashboardStore'
import ErrorAlert from '../components/common/ErrorAlert'
import LoadingOverlay from '../components/common/LoadingOverlay'
import ScoreGauge from '../components/common/ScoreGauge'
import StatusChip from '../components/common/StatusChip'
import EmptyState from '../components/common/EmptyState'
import type { Application, ApplicationCreate } from '../types/dashboard'

const KANBAN_COLUMNS = [
  { key: '待评估', label: '待评估', color: '#9ca3af' },
  { key: '已评估', label: '已评估', color: '#3B82F6' },
  { key: '准备中', label: '准备中', color: '#8B5CF6' },
  { key: '已投递', label: '已投递', color: '#F59E0B' },
  { key: '面试中', label: '面试中', color: '#06B6D4' },
  { key: '已offer', label: '已offer', color: '#10B981' },
  { key: '已拒绝', label: '已拒绝', color: '#EF4444' },
  { key: '放弃', label: '放弃', color: '#6b7280' },
]

const PIE_COLORS = ['#9ca3af', '#3B82F6', '#8B5CF6', '#F59E0B', '#06B6D4', '#10B981', '#EF4444', '#6b7280']

const ALL_STATUSES = KANBAN_COLUMNS.map((c) => c.key)

export default function DashboardPage() {
  const {
    applications, stats, loading, error, selectedApp,
    fetchApplications, fetchStats, createApplication, updateApplication,
    deleteApplication, selectApp, clearError,
  } = useDashboardStore()

  const [addOpen, setAddOpen] = useState(false)
  const [newApp, setNewApp] = useState({ job_id: '', job_title: '', company_name: '' })

  useEffect(() => {
    fetchApplications()
    fetchStats()
  }, [fetchApplications, fetchStats])

  const handleCreate = async () => {
    if (!newApp.job_title || !newApp.company_name) return
    await createApplication({
      job_id: newApp.job_id || `manual_${Date.now()}`,
      job_title: newApp.job_title,
      company_name: newApp.company_name,
      status: '待评估',
    })
    setNewApp({ job_id: '', job_title: '', company_name: '' })
    setAddOpen(false)
  }

  const handleStatusChange = async (appId: string, newStatus: string) => {
    await updateApplication(appId, { status: newStatus })
    if (selectedApp?.id === appId) {
      selectApp({ ...selectedApp, status: newStatus })
    }
  }

  const pieData = stats
    ? Object.entries(stats.by_status).map(([name, value]) => ({ name, value }))
    : []

  const radarData = stats
    ? Object.entries(stats.top_dimension_scores).map(([key, val]) => ({
        dimension: key,
        score: val,
        fullMark: 100,
      }))
    : []

  const getAppsByStatus = (status: string) =>
    applications.filter((app) => app.status === status)

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">求职看板</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setAddOpen(true)}>
          新增投递
        </Button>
      </Box>

      <ErrorAlert error={error} onClose={clearError} />

      <Box sx={{ display: 'flex', gap: 3 }}>
        {/* Main Area - Kanban Board */}
        <Box sx={{ flex: 1, position: 'relative', minHeight: 500, overflow: 'auto' }}>
          <LoadingOverlay loading={loading} message="加载中..." />

          {applications.length === 0 && !loading ? (
            <EmptyState
              title="暂无投递记录"
              description={'点击「新增投递」开始追踪你的求职进度'}
              action={{ label: '新增投递', onClick: () => setAddOpen(true) }}
            />
          ) : (
            <Box sx={{ display: 'flex', gap: 1.5, overflowX: 'auto', pb: 2 }}>
              {KANBAN_COLUMNS.map((col) => {
                const colApps = getAppsByStatus(col.key)
                return (
                  <Paper
                    key={col.key}
                    sx={{
                      minWidth: 220,
                      maxWidth: 220,
                      borderTop: `3px solid ${col.color}`,
                      p: 1.5,
                      flexShrink: 0,
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="subtitle2" fontWeight={600}>{col.label}</Typography>
                      <Chip label={colApps.length} size="small" sx={{ bgcolor: col.color, color: '#fff', height: 20, fontSize: 11 }} />
                    </Box>
                    <Stack spacing={1}>
                      {colApps.map((app) => (
                        <Card
                          key={app.id}
                          variant="outlined"
                          sx={{
                            cursor: 'pointer',
                            '&:hover': { boxShadow: 2 },
                          }}
                          onClick={() => selectApp(app)}
                        >
                          <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                            <Typography variant="body2" fontWeight={600} noWrap>
                              {app.company_name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary" noWrap display="block">
                              {app.job_title}
                            </Typography>
                            {app.match_score !== null && (
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
                                <Box
                                  sx={{
                                    width: 6,
                                    height: 6,
                                    borderRadius: '50%',
                                    bgcolor: app.match_score >= 80 ? '#10B981' : app.match_score >= 60 ? '#3B82F6' : '#F59E0B',
                                  }}
                                />
                                <Typography variant="caption" fontWeight={600}>{app.match_score}分</Typography>
                              </Box>
                            )}
                            {app.next_action && (
                              <Typography variant="caption" color="primary.main" sx={{ mt: 0.5, display: 'block' }}>
                                {app.next_action}
                              </Typography>
                            )}
                          </CardContent>
                        </Card>
                      ))}
                    </Stack>
                  </Paper>
                )
              })}
            </Box>
          )}
        </Box>

        {/* Stats Sidebar */}
        {stats && (
          <Box sx={{ width: 280, flexShrink: 0 }}>
            <Stack spacing={2}>
              {/* Summary Cards */}
              <Card>
                <CardContent>
                  <Typography variant="subtitle2" color="text.secondary">总投递数</Typography>
                  <Typography variant="h4" fontWeight={700}>{stats.total}</Typography>
                </CardContent>
              </Card>

              <Card>
                <CardContent>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">面试率</Typography>
                      <Typography variant="h6" fontWeight={700}>
                        {Math.round(stats.interview_rate * 100)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Offer率</Typography>
                      <Typography variant="h6" fontWeight={700}>
                        {Math.round(stats.offer_rate * 100)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="caption" color="text.secondary">平均匹配分</Typography>
                      <Typography variant="h6" fontWeight={700}>
                        {Math.round(stats.avg_match_score)}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>

              {/* Pie Chart */}
              {pieData.length > 0 && (
                <Card>
                  <CardContent>
                    <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>状态分布</Typography>
                    <ResponsiveContainer width="100%" height={180}>
                      <PieChart>
                        <Pie
                          data={pieData}
                          cx="50%"
                          cy="50%"
                          innerRadius={35}
                          outerRadius={70}
                          dataKey="value"
                          label={({ name, value }) => `${name} ${value}`}
                        >
                          {pieData.map((_, i) => (
                            <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                          ))}
                        </Pie>
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              )}

              {/* Radar Chart */}
              {radarData.length > 0 && (
                <Card>
                  <CardContent>
                    <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>各维度平均分</Typography>
                    <ResponsiveContainer width="100%" height={200}>
                      <RadarChart data={radarData}>
                        <PolarGrid />
                        <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 10 }} />
                        <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} />
                        <Radar
                          dataKey="score"
                          stroke="#3B82F6"
                          fill="#3B82F6"
                          fillOpacity={0.3}
                        />
                        <ReTooltip />
                      </RadarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              )}
            </Stack>
          </Box>
        )}
      </Box>

      {/* Detail Modal */}
      <Dialog
        open={!!selectedApp}
        onClose={() => selectApp(null)}
        maxWidth="sm"
        fullWidth
      >
        {selectedApp && (
          <>
            <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              {selectedApp.company_name} - {selectedApp.job_title}
              <IconButton onClick={() => selectApp(null)}><CloseIcon /></IconButton>
            </DialogTitle>
            <DialogContent dividers>
              <Stack spacing={2}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <StatusChip status={selectedApp.status} />
                  {selectedApp.match_score !== null && (
                    <Typography variant="body2" fontWeight={600}>
                      匹配分: {selectedApp.match_score}
                    </Typography>
                  )}
                </Box>

                <Box>
                  <Typography variant="subtitle2" sx={{ mb: 0.5 }}>状态变更</Typography>
                  <FormControl size="small" fullWidth>
                    <Select
                      value={selectedApp.status}
                      onChange={(e) => handleStatusChange(selectedApp.id, e.target.value)}
                    >
                      {ALL_STATUSES.map((s) => (
                        <MenuItem key={s} value={s}>{s}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Box>

                {selectedApp.next_action && (
                  <Box>
                    <Typography variant="subtitle2" color="text.secondary">下一步行动</Typography>
                    <Typography variant="body2">{selectedApp.next_action}</Typography>
                    {selectedApp.next_action_deadline && (
                      <Typography variant="caption" color="error.main">
                        截止: {new Date(selectedApp.next_action_deadline).toLocaleDateString()}
                      </Typography>
                    )}
                  </Box>
                )}

                {selectedApp.notes && (
                  <Box>
                    <Typography variant="subtitle2" color="text.secondary">备注</Typography>
                    <Typography variant="body2">{selectedApp.notes}</Typography>
                  </Box>
                )}

                {selectedApp.tags.length > 0 && (
                  <Stack direction="row" spacing={0.5} sx={{ flexWrap: 'wrap', gap: 0.5 }}>
                    {selectedApp.tags.map((tag) => (
                      <Chip key={tag} label={tag} size="small" variant="outlined" />
                    ))}
                  </Stack>
                )}

                {/* Timeline */}
                {selectedApp.timeline.length > 0 && (
                  <Box>
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>时间线</Typography>
                    <Stack spacing={1}>
                      {selectedApp.timeline.map((entry, i) => (
                        <Box key={i} sx={{ display: 'flex', gap: 1.5, alignItems: 'flex-start' }}>
                          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: 'primary.main', mt: 0.5 }} />
                            {i < selectedApp.timeline.length - 1 && (
                              <Box sx={{ width: 2, flex: 1, bgcolor: 'divider', minHeight: 20 }} />
                            )}
                          </Box>
                          <Box>
                            <Typography variant="caption" color="text.disabled">
                              {new Date(entry.time).toLocaleString()}
                            </Typography>
                            <Typography variant="body2" fontWeight={600}>{entry.action}</Typography>
                            <Typography variant="body2" color="text.secondary">{entry.detail}</Typography>
                          </Box>
                        </Box>
                      ))}
                    </Stack>
                  </Box>
                )}
              </Stack>
            </DialogContent>
            <DialogActions>
              <Button
                color="error"
                startIcon={<DeleteIcon />}
                onClick={() => {
                  deleteApplication(selectedApp.id)
                  selectApp(null)
                }}
              >
                删除
              </Button>
              <Button onClick={() => selectApp(null)}>关闭</Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* Add Application Dialog */}
      <Dialog open={addOpen} onClose={() => setAddOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>新增投递</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="公司名称"
              value={newApp.company_name}
              onChange={(e) => setNewApp((prev) => ({ ...prev, company_name: e.target.value }))}
              fullWidth
              required
            />
            <TextField
              label="岗位名称"
              value={newApp.job_title}
              onChange={(e) => setNewApp((prev) => ({ ...prev, job_title: e.target.value }))}
              fullWidth
              required
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddOpen(false)}>取消</Button>
          <Button
            variant="contained"
            onClick={handleCreate}
            disabled={!newApp.company_name || !newApp.job_title}
          >
            创建
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
