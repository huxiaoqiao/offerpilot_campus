import { useState } from 'react'
import { Box } from '@mui/material'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

const SIDEBAR_WIDTH = 240
const SIDEBAR_COLLAPSED_WIDTH = 64
const HEADER_HEIGHT = 64

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const sidebarWidth = collapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH

  return (
    <Box sx={{ display: 'flex', height: '100vh', bgcolor: '#f8fafc' }}>
      <Sidebar width={sidebarWidth} collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <Header sidebarWidth={sidebarWidth} headerHeight={HEADER_HEIGHT} />
        <Box
          component="main"
          sx={{
            flex: 1,
            p: 3,
            mt: `${HEADER_HEIGHT}px`,
            ml: `${sidebarWidth}px`,
            overflow: 'auto',
            transition: 'margin-left 0.2s ease',
          }}
        >
          <Outlet />
        </Box>
      </Box>
    </Box>
  )
}
