import { Box, CircularProgress, Typography } from '@mui/material'

interface LoadingOverlayProps {
  loading: boolean
  message?: string
}

export default function LoadingOverlay({ loading, message }: LoadingOverlayProps) {
  if (!loading) return null
  return (
    <Box
      sx={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'rgba(255,255,255,0.7)',
        zIndex: 10,
        borderRadius: 1,
      }}
    >
      <CircularProgress size={40} />
      {message && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          {message}
        </Typography>
      )}
    </Box>
  )
}
