import { useState, useEffect, useCallback } from 'react'
import {
  Box, Typography, Stepper, Step, StepLabel, Button, TextField, Chip,
  Slider, Card, CardContent, Avatar, Stack, IconButton, Autocomplete,
  CircularProgress, Paper, Divider,
} from '@mui/material'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import PersonIcon from '@mui/icons-material/Person'
import WorkOutlineIcon from '@mui/icons-material/WorkOutline'
import SchoolIcon from '@mui/icons-material/School'
import { useProfileStore } from '../store/profileStore'
import ErrorAlert from '../components/common/ErrorAlert'
import LoadingOverlay from '../components/common/LoadingOverlay'
import EmptyState from '../components/common/EmptyState'
import type { ProfileCreate } from '../types/profile'

const STEPS = ['上传简历', '基本信息', '求职偏好']

const GRADE_OPTIONS = ['大一', '大二', '大三', '大四', '研一', '研二', '研三', '博士']
const POSITION_OPTIONS = ['前端开发', '后端开发', '全栈开发', '产品经理', '数据分析师', '算法工程师', '测试工程师', '运维工程师', 'UI设计师', '运营']
const CITY_OPTIONS = ['北京', '上海', '广州', '深圳', '杭州', '成都', '南京', '武汉', '西安', '苏州', '长沙', '重庆']
const INDUSTRY_OPTIONS = ['互联网', '金融', '教育', '医疗', '电商', '游戏', '人工智能', '新能源', '汽车', '咨询']
const AVOID_OPTIONS = ['大小周', '996', '出差频繁', '外包', '初创公司', '异地办公', '夜班', '高压KPI']

export default function ProfilePage() {
  const { profile, loading, error, fetchProfile, createProfile, updateProfile, uploadResume, clearError } = useProfileStore()
  const [activeStep, setActiveStep] = useState(0)
  const [profileId, setProfileId] = useState<string | null>(null)

  // Form state
  const [name, setName] = useState('')
  const [school, setSchool] = useState('')
  const [major, setMajor] = useState('')
  const [grade, setGrade] = useState('')
  const [graduationYear, setGraduationYear] = useState<number>(new Date().getFullYear() + 1)
  const [targetPositions, setTargetPositions] = useState<string[]>([])
  const [targetCities, setTargetCities] = useState<string[]>([])
  const [salaryRange, setSalaryRange] = useState<number[]>([8, 25])
  const [targetIndustries, setTargetIndustries] = useState<string[]>([])
  const [avoidItems, setAvoidItems] = useState<string[]>([])
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    const storedId = localStorage.getItem('offerpilot_profile_id')
    if (storedId) {
      setProfileId(storedId)
      fetchProfile(storedId)
    }
  }, [fetchProfile])

  useEffect(() => {
    if (profile) {
      setName(profile.name || '')
      setSchool(profile.school || '')
      setMajor(profile.major || '')
      setGrade(profile.grade || '')
      setGraduationYear(profile.graduation_year || new Date().getFullYear() + 1)
      setTargetPositions(profile.target_positions || [])
      setTargetCities(profile.target_cities || [])
      setSalaryRange([profile.salary_min ?? 8, profile.salary_max ?? 25])
      setTargetIndustries(profile.target_industries || [])
      setAvoidItems(profile.avoid_items || [])
    }
  }, [profile])

  const handleFileUpload = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !profileId) return
    setUploading(true)
    try {
      await uploadResume(profileId, file)
    } finally {
      setUploading(false)
    }
  }, [profileId, uploadResume])

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (!file || !profileId) return
    setUploading(true)
    try {
      await uploadResume(profileId, file)
    } finally {
      setUploading(false)
    }
  }, [profileId, uploadResume])

  const handleCreateProfile = async () => {
    const data: ProfileCreate = {
      name,
      school,
      major,
      grade,
      graduation_year: graduationYear,
      target_positions: targetPositions,
      target_cities: targetCities,
      salary_min: salaryRange[0],
      salary_max: salaryRange[1],
      target_industries: targetIndustries,
      avoid_items: avoidItems,
    }
    const id = await createProfile(data)
    setProfileId(id)
    localStorage.setItem('offerpilot_profile_id', id)
  }

  const handleUpdateProfile = async () => {
    if (!profileId) return
    await updateProfile(profileId, {
      name, school, major, grade,
      graduation_year: graduationYear,
      target_positions: targetPositions,
      target_cities: targetCities,
      salary_min: salaryRange[0],
      salary_max: salaryRange[1],
      target_industries: targetIndustries,
      avoid_items: avoidItems,
    })
  }

  const handleNext = async () => {
    if (activeStep === 1 && !profileId) {
      await handleCreateProfile()
    } else if (activeStep === 2) {
      await handleUpdateProfile()
    }
    setActiveStep((prev) => prev + 1)
  }

  const handleBack = () => setActiveStep((prev) => prev - 1)

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>求职画像</Typography>
      <ErrorAlert error={error} onClose={clearError} />

      {/* Profile Summary Card */}
      {profile && (
        <Card sx={{ mb: 3 }}>
          <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ width: 56, height: 56, bgcolor: 'primary.main' }}>
              {profile.name?.[0] || '?'}
            </Avatar>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6">{profile.name || '未设置姓名'}</Typography>
              <Typography variant="body2" color="text.secondary">
                {profile.school} · {profile.major} · {profile.grade}
              </Typography>
              <Stack direction="row" spacing={1} sx={{ mt: 0.5, flexWrap: 'wrap', gap: 0.5 }}>
                {profile.target_positions?.map((p) => (
                  <Chip key={p} label={p} size="small" color="primary" variant="outlined" />
                ))}
              </Stack>
            </Box>
            <Button variant="outlined" size="small" onClick={() => setActiveStep(0)}>
              编辑资料
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Stepper */}
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {STEPS.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <Box sx={{ position: 'relative', minHeight: 400 }}>
        <LoadingOverlay loading={loading} message="处理中..." />

        {/* Step 0: Upload Resume */}
        {activeStep === 0 && (
          <Box>
            <Typography variant="h6" sx={{ mb: 2 }}>上传简历</Typography>
            <Paper
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              sx={{
                p: 6,
                textAlign: 'center',
                border: '2px dashed',
                borderColor: 'divider',
                borderRadius: 2,
                cursor: 'pointer',
                '&:hover': { borderColor: 'primary.main', bgcolor: 'action.hover' },
              }}
            >
              <input
                type="file"
                accept=".pdf,.doc,.docx,.txt,.md"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
                id="resume-upload"
              />
              <label htmlFor="resume-upload" style={{ cursor: 'pointer' }}>
                <CloudUploadIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
                <Typography variant="h6" color="text.secondary">
                  {uploading ? '上传中...' : '拖拽简历到此处，或点击选择文件'}
                </Typography>
                <Typography variant="body2" color="text.disabled">
                  支持 PDF、DOCX、TXT、MD 格式
                </Typography>
              </label>
            </Paper>

            {profile?.resume_structured && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 600 }}>
                  解析结果预览
                </Typography>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>
                      教育背景
                    </Typography>
                    {profile.resume_structured.education.map((edu, i) => (
                      <Typography key={i} variant="body2" color="text.secondary">
                        {edu.school} · {edu.major} · {edu.degree} ({edu.start_date} ~ {edu.end_date})
                      </Typography>
                    ))}
                    <Divider sx={{ my: 1.5 }} />
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>技能</Typography>
                    <Stack direction="row" spacing={0.5} sx={{ flexWrap: 'wrap', gap: 0.5 }}>
                      {profile.resume_structured.skills.map((s) => (
                        <Chip key={s} label={s} size="small" />
                      ))}
                    </Stack>
                    <Divider sx={{ my: 1.5 }} />
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>经历</Typography>
                    {profile.resume_structured.experiences.map((exp, i) => (
                      <Box key={i} sx={{ mb: 1 }}>
                        <Typography variant="body2" fontWeight={600}>
                          [{exp.type}] {exp.title} @ {exp.organization}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {exp.description}
                        </Typography>
                      </Box>
                    ))}
                  </CardContent>
                </Card>
              </Box>
            )}

            {!profileId && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                提示：请先在下一步填写基本信息创建画像后再上传简历。
              </Typography>
            )}
          </Box>
        )}

        {/* Step 1: Basic Info */}
        {activeStep === 1 && (
          <Box sx={{ maxWidth: 600 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>基本信息</Typography>
            <Stack spacing={2.5}>
              <TextField
                label="姓名"
                value={name}
                onChange={(e) => setName(e.target.value)}
                fullWidth
                required
              />
              <TextField
                label="学校"
                value={school}
                onChange={(e) => setSchool(e.target.value)}
                fullWidth
                required
              />
              <TextField
                label="专业"
                value={major}
                onChange={(e) => setMajor(e.target.value)}
                fullWidth
                required
              />
              <Autocomplete
                options={GRADE_OPTIONS}
                value={grade}
                onChange={(_, v) => setGrade(v || '')}
                renderInput={(params) => <TextField {...params} label="年级" required />}
              />
              <TextField
                label="毕业年份"
                type="number"
                value={graduationYear}
                onChange={(e) => setGraduationYear(Number(e.target.value))}
                fullWidth
                required
              />
            </Stack>
          </Box>
        )}

        {/* Step 2: Job Preferences */}
        {activeStep === 2 && (
          <Box sx={{ maxWidth: 600 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>求职偏好</Typography>
            <Stack spacing={3}>
              <Box>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>目标岗位类型</Typography>
                <Stack direction="row" spacing={0.5} sx={{ flexWrap: 'wrap', gap: 0.5 }}>
                  {POSITION_OPTIONS.map((pos) => (
                    <Chip
                      key={pos}
                      label={pos}
                      clickable
                      color={targetPositions.includes(pos) ? 'primary' : 'default'}
                      variant={targetPositions.includes(pos) ? 'filled' : 'outlined'}
                      onClick={() =>
                        setTargetPositions((prev) =>
                          prev.includes(pos) ? prev.filter((p) => p !== pos) : [...prev, pos]
                        )
                      }
                    />
                  ))}
                </Stack>
              </Box>

              <Box>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>目标城市</Typography>
                <Stack direction="row" spacing={0.5} sx={{ flexWrap: 'wrap', gap: 0.5 }}>
                  {CITY_OPTIONS.map((city) => (
                    <Chip
                      key={city}
                      label={city}
                      clickable
                      color={targetCities.includes(city) ? 'primary' : 'default'}
                      variant={targetCities.includes(city) ? 'filled' : 'outlined'}
                      onClick={() =>
                        setTargetCities((prev) =>
                          prev.includes(city) ? prev.filter((c) => c !== city) : [...prev, city]
                        )
                      }
                    />
                  ))}
                </Stack>
              </Box>

              <Box>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  期望薪资范围（K/月）: {salaryRange[0]}K ~ {salaryRange[1]}K
                </Typography>
                <Slider
                  value={salaryRange}
                  onChange={(_, v) => setSalaryRange(v as number[])}
                  valueLabelDisplay="auto"
                  min={3}
                  max={80}
                  step={1}
                />
              </Box>

              <Box>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>目标行业</Typography>
                <Stack direction="row" spacing={0.5} sx={{ flexWrap: 'wrap', gap: 0.5 }}>
                  {INDUSTRY_OPTIONS.map((ind) => (
                    <Chip
                      key={ind}
                      label={ind}
                      clickable
                      color={targetIndustries.includes(ind) ? 'secondary' : 'default'}
                      variant={targetIndustries.includes(ind) ? 'filled' : 'outlined'}
                      onClick={() =>
                        setTargetIndustries((prev) =>
                          prev.includes(ind) ? prev.filter((i) => i !== ind) : [...prev, ind]
                        )
                      }
                    />
                  ))}
                </Stack>
              </Box>

              <Box>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>避雷项</Typography>
                <Stack direction="row" spacing={0.5} sx={{ flexWrap: 'wrap', gap: 0.5 }}>
                  {AVOID_OPTIONS.map((item) => (
                    <Chip
                      key={item}
                      label={item}
                      clickable
                      color={avoidItems.includes(item) ? 'error' : 'default'}
                      variant={avoidItems.includes(item) ? 'filled' : 'outlined'}
                      onClick={() =>
                        setAvoidItems((prev) =>
                          prev.includes(item) ? prev.filter((a) => a !== item) : [...prev, item]
                        )
                      }
                    />
                  ))}
                </Stack>
              </Box>
            </Stack>
          </Box>
        )}

        {/* Completion */}
        {activeStep === 3 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h5" sx={{ mb: 1 }}>画像创建完成！</Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              你的求职画像已保存，可以前往其他功能模块开始使用。
            </Typography>
            <Button variant="contained" onClick={() => setActiveStep(0)}>
              编辑画像
            </Button>
          </Box>
        )}
      </Box>

      {/* Navigation Buttons */}
      {activeStep < 3 && (
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
          <Button disabled={activeStep === 0} onClick={handleBack}>
            上一步
          </Button>
          <Button
            variant="contained"
            onClick={handleNext}
            disabled={loading || (activeStep === 1 && (!name || !school || !major || !grade))}
          >
            {activeStep === 2 ? '完成' : '下一步'}
          </Button>
        </Box>
      )}
    </Box>
  )
}
