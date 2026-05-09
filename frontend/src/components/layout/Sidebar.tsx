import { useLocation, useNavigate } from 'react-router-dom'
import {
  Box,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  IconButton,
  Tooltip,
} from '@mui/material'
import PersonIcon from '@mui/icons-material/Person'
import WorkIcon from '@mui/icons-material/Work'
import CompareArrowsIcon from '@mui/icons-material/CompareArrows'
import DescriptionIcon from '@mui/icons-material/Description'
import PsychologyIcon from '@mui/icons-material/Psychology'
import QuizIcon from '@mui/icons-material/Quiz'
import DashboardIcon from '@mui/icons-material/Dashboard'
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft'
import ChevronRightIcon from '@mui/icons-material/ChevronRight'

const navItems = [
  { label: '求职画像', icon: <PersonIcon />, path: '/profile' },
  { label: '岗位雷达', icon: <WorkIcon />, path: '/jobs' },
  { label: '匹配解释', icon: <CompareArrowsIcon />, path: '/match' },
  { label: '简历改写', icon: <DescriptionIcon />, path: '/resume' },
  { label: 'HR模拟器', icon: <PsychologyIcon />, path: '/hr' },
  { label: '面试训练', icon: <QuizIcon />, path: '/interview' },
  { label: '求职看板', icon: <DashboardIcon />, path: '/dashboard' },
]

interface SidebarProps {
  width: number
  collapsed: boolean
  onToggle: () => void
}

export default function Sidebar({ width, collapsed, onToggle }: SidebarProps) {
  const location = useLocation()
  const navigate = useNavigate()

  const isActive = (path: string) => {
    const currentPath = location.pathname
    if (path === '/profile') return currentPath === '/profile'
    return currentPath.startsWith(path)
  }

  return (
    <Box
      component="nav"
      sx={{
        width: `${width}px`,
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        bgcolor: '#ffffff',
        borderRight: '1px solid #e2e8f0',
        display: 'flex',
        flexDirection: 'column',
        transition: 'width 0.2s ease',
        zIndex: 1200,
        overflow: 'hidden',
      }}
    >
      {/* Logo area */}
      <Box
        sx={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'flex-start',
          px: collapsed ? 1 : 2.5,
          borderBottom: '1px solid #e2e8f0',
          flexShrink: 0,
        }}
      >
        {collapsed ? (
          <Typography variant="h6" sx={{ color: '#3B82F6', fontWeight: 700 }}>
            OP
          </Typography>
        ) : (
          <Typography variant="h6" sx={{ color: '#3B82F6', fontWeight: 700 }}>
            OfferPilot
          </Typography>
        )}
      </Box>

      {/* Nav list */}
      <List sx={{ flex: 1, py: 1, px: 0.5 }}>
        {navItems.map((item) => {
          const active = isActive(item.path)
          return (
            <Tooltip
              key={item.path}
              title={collapsed ? item.label : ''}
              placement="right"
              arrow
            >
              <ListItemButton
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: '8px',
                  mb: 0.5,
                  minHeight: 44,
                  justifyContent: collapsed ? 'center' : 'flex-start',
                  px: collapsed ? 1 : 2,
                  bgcolor: active ? '#eff6ff' : 'transparent',
                  color: active ? '#2563eb' : '#64748b',
                  '&:hover': {
                    bgcolor: active ? '#dbeafe' : '#f1f5f9',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: collapsed ? 0 : 40,
                    justifyContent: 'center',
                    color: active ? '#3B82F6' : '#94a3b8',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                {!collapsed && (
                  <ListItemText
                    primary={item.label}
                    primaryTypographyProps={{
                      fontSize: 14,
                      fontWeight: active ? 600 : 400,
                    }}
                  />
                )}
              </ListItemButton>
            </Tooltip>
          )
        })}
      </List>

      {/* Bottom section */}
      <Box
        sx={{
          p: collapsed ? 1 : 2,
          borderTop: '1px solid #e2e8f0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'space-between',
          flexShrink: 0,
        }}
      >
        {!collapsed && (
          <Typography variant="caption" sx={{ color: '#94a3b8' }}>
            OfferPilot v1.0.0
          </Typography>
        )}
        <IconButton size="small" onClick={onToggle} sx={{ color: '#94a3b8' }}>
          {collapsed ? <ChevronRightIcon fontSize="small" /> : <ChevronLeftIcon fontSize="small" />}
        </IconButton>
      </Box>
    </Box>
  )
}
