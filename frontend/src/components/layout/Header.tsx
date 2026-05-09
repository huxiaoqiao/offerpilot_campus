import { useLocation } from 'react-router-dom'
import { Box, Typography, Breadcrumbs, Link, Avatar, IconButton } from '@mui/material'
import SettingsIcon from '@mui/icons-material/Settings'
import NavigateNextIcon from '@mui/icons-material/NavigateNext'

const pathNameMap: Record<string, string> = {
  profile: '求识画像',
  jobs: '岗位雷达',
  match: '匹配解释',
  resume: '简历改写',
  hr: 'HR模拟器',
  interview: '面试训练',
  dashboard: '求职看板',
}

interface HeaderProps {
  sidebarWidth: number
  headerHeight: number
}

export default function Header({ sidebarWidth, headerHeight }: HeaderProps) {
  const location = useLocation()
  const pathSegments = location.pathname.split('/').filter(Boolean)
  const currentPage = pathSegments[0] || 'profile'
  const pageName = pathNameMap[currentPage] || currentPage

  return (
    <Box
      component="header"
      sx={{
        position: 'fixed',
        top: 0,
        left: `${sidebarWidth}px`,
        right: 0,
        height: `${headerHeight}px`,
        bgcolor: '#ffffff',
        borderBottom: '1px solid #e2e8f0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        px: 3,
        zIndex: 1100,
        transition: 'left 0.2s ease',
      }}
    >
      {/* Left: Breadcrumbs */}
      <Breadcrumbs separator={<NavigateNextIcon fontSize="small" />} aria-label="breadcrumb">
        <Link
          underline="hover"
          color="inherit"
          href="/"
          sx={{ fontSize: 14, color: '#94a3b8' }}
        >
          OfferPilot
        </Link>
        <Typography sx={{ fontSize: 14, fontWeight: 600, color: '#1e293b' }}>
          {pageName}
        </Typography>
      </Breadcrumbs>

      {/* Right: User avatar + settings */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <IconButton size="small" sx={{ color: '#94a3b8' }}>
          <SettingsIcon fontSize="small" />
        </IconButton>
        <Avatar
          sx={{
            width: 32,
            height: 32,
            bgcolor: '#3B82F6',
            fontSize: 14,
          }}
        >
          U
        </Avatar>
      </Box>
    </Box>
  )
}
