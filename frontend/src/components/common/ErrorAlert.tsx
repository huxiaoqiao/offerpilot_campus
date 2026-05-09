import { Alert, IconButton } from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'

interface ErrorAlertProps {
  error: string | null
  onClose: () => void
}

export default function ErrorAlert({ error, onClose }: ErrorAlertProps) {
  if (!error) return null
  return (
    <Alert
      severity="error"
      sx={{ mb: 2 }}
      action={
        <IconButton size="small" onClick={onClose}>
          <CloseIcon fontSize="inherit" />
        </IconButton>
      }
    >
      {error}
    </Alert>
  )
}
