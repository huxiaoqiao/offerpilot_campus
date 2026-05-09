export function createSSEConnection(
  url: string,
  onMessage: (data: string) => void,
  onDone?: () => void,
  onError?: (err: Error) => void
) {
  const eventSource = new EventSource(url)
  eventSource.onmessage = (event) => onMessage(event.data)
  eventSource.onerror = () => {
    onError?.(new Error('SSE connection error'))
    eventSource.close()
  }
  if (onDone) {
    eventSource.addEventListener('done', () => {
      onDone()
      eventSource.close()
    })
  }
  return () => eventSource.close()
}
