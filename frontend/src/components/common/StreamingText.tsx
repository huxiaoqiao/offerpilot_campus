import { useState, useEffect, useRef } from 'react'
import { Box, Typography } from '@mui/material'

interface StreamingTextProps {
  text: string
  speed?: number
}

export default function StreamingText({ text, speed = 30 }: StreamingTextProps) {
  const [displayed, setDisplayed] = useState('')
  const indexRef = useRef(0)

  useEffect(() => {
    setDisplayed('')
    indexRef.current = 0
    if (!text) return

    const interval = setInterval(() => {
      indexRef.current += 1
      if (indexRef.current >= text.length) {
        setDisplayed(text)
        clearInterval(interval)
      } else {
        setDisplayed(text.slice(0, indexRef.current))
      }
    }, speed)

    return () => clearInterval(interval)
  }, [text, speed])

  return (
    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
      {displayed}
      {displayed.length < text.length && (
        <Box component="span" sx={{ animation: 'blink 1s step-end infinite' }}>|</Box>
      )}
    </Typography>
  )
}
