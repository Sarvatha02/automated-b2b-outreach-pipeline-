import { useState, useEffect, useRef, useCallback } from 'react'
import { getPipelineStatus } from '../utils/api'

const TERMINAL_STATES = ['completed', 'failed', 'awaiting_approval']

export function usePipelineStatus(pipelineId, interval = 2000) {
  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)
  const timerRef = useRef(null)

  const fetch = useCallback(async () => {
    if (!pipelineId) return
    try {
      const data = await getPipelineStatus(pipelineId)
      setStatus(data)
      if (TERMINAL_STATES.includes(data.status)) {
        clearInterval(timerRef.current)
      }
    } catch (e) {
      setError(e.message)
    }
  }, [pipelineId])

  useEffect(() => {
    if (!pipelineId) return
    fetch()
    timerRef.current = setInterval(fetch, interval)
    return () => clearInterval(timerRef.current)
  }, [pipelineId, interval, fetch])

  return { status, error, refetch: fetch }
}
