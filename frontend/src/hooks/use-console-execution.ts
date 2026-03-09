'use client'

import { useCallback } from 'react'
import { useStore } from '@/lib/stores/context'
import type {
  AgentResult,
  AgentError,
  StreamFrame,
  ChatMessageRequest,
  ChatExecuteRequest,
  AgentRunRequest,
} from '@/lib/api/contracts/agent'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * Endpoint path mapping
 */
const ENDPOINT_PATHS = {
  'chat-message': '/api/v1/chat/message',
  'chat-execute': '/api/v1/chat/execute',
  'agent-run': '/api/v1/agent/run',
} as const

/**
 * useConsoleExecution - Hook for console execution operations
 *
 * CONS-07: Execute button triggers sync + SSE streaming
 * CONS-12: SSE streaming execution support
 *
 * Handles both synchronous requests and SSE streaming.
 */
export function useConsoleExecution() {
  // Get store state and actions
  const endpoint = useStore((state) => state.endpoint)
  const mode = useStore((state) => state.mode)
  const message = useStore((state) => state.message)
  const modelText = useStore((state) => state.modelText)
  const includeModel = useStore((state) => state.includeModel)
  const analysisType = useStore((state) => state.analysisType)
  const reportFormat = useStore((state) => state.reportFormat)
  const reportOutput = useStore((state) => state.reportOutput)
  const autoAnalyze = useStore((state) => state.autoAnalyze)
  const autoCodeCheck = useStore((state) => state.autoCodeCheck)
  const includeReport = useStore((state) => state.includeReport)
  const conversationId = useStore((state) => state.conversationId)
  const traceId = useStore((state) => state.traceId)

  const setLoading = useStore((state) => state.setLoading)
  const setConnectionState = useStore((state) => state.setConnectionState)
  const setResult = useStore((state) => state.setResult)
  const setRawResponse = useStore((state) => state.setRawResponse)
  const setStreamFrames = useStore((state) => state.setStreamFrames)
  const setError = useStore((state) => state.setError)

  /**
   * Validate model JSON if includeModel is true
   */
  const validateModelJson = useCallback((): { valid: boolean; error?: string } => {
    if (!includeModel) {
      return { valid: true }
    }

    if (!modelText.trim()) {
      return { valid: false, error: 'Model JSON is required when includeModel is enabled' }
    }

    try {
      JSON.parse(modelText)
      return { valid: true }
    } catch {
      return { valid: false, error: 'Invalid JSON in model text' }
    }
  }, [includeModel, modelText])

  /**
   * Build request payload based on endpoint type
   */
  const buildPayload = useCallback(() => {
    const context = includeModel ? { modelText, includeModel } : undefined

    const basePayload = {
      message,
      conversationId,
      traceId,
      context,
    }

    switch (endpoint) {
      case 'chat-message':
        return basePayload as ChatMessageRequest

      case 'chat-execute':
        return {
          ...basePayload,
          mode,
        } as ChatExecuteRequest

      case 'agent-run':
        return {
          ...basePayload,
          mode,
          analysisType,
          reportFormat,
          reportOutput,
          autoAnalyze,
          autoCodeCheck,
          includeReport,
        } as AgentRunRequest

      default:
        return basePayload
    }
  }, [
    endpoint,
    mode,
    message,
    modelText,
    includeModel,
    analysisType,
    reportFormat,
    reportOutput,
    autoAnalyze,
    autoCodeCheck,
    includeReport,
    conversationId,
    traceId,
  ])

  /**
   * Execute synchronous request
   */
  const executeSync = useCallback(async (): Promise<{ success: boolean; error?: string }> => {
    // Validate model JSON if needed
    const validation = validateModelJson()
    if (!validation.valid) {
      setError({ message: validation.error! })
      return { success: false, error: validation.error }
    }

    // Clear previous state
    setLoading(true)
    setConnectionState('connecting')
    setError(null)
    setResult(null)
    setRawResponse(null)
    setStreamFrames([])

    const payload = buildPayload()
    const path = ENDPOINT_PATHS[endpoint]

    try {
      const response = await fetch(`${API_BASE}${path}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        let errorData: AgentError
        try {
          errorData = await response.json()
        } catch {
          errorData = { message: `${response.status} ${response.statusText}` }
        }

        setError(errorData)
        setConnectionState('error')
        setLoading(false)
        return { success: false, error: errorData.message }
      }

      const data = await response.json()
      setRawResponse(data)

      // Parse as AgentResult
      const result: AgentResult = {
        response: data.response || data.message || '',
        conversationId: data.conversationId,
        traceId: data.traceId,
        data: data.data,
      }

      setResult(result)
      setConnectionState('connected')
      setLoading(false)
      return { success: true }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred'
      setError({ message: errorMessage })
      setConnectionState('error')
      setLoading(false)
      return { success: false, error: errorMessage }
    }
  }, [
    endpoint,
    validateModelJson,
    buildPayload,
    setLoading,
    setConnectionState,
    setError,
    setResult,
    setRawResponse,
    setStreamFrames,
  ])

  /**
   * Execute SSE streaming request
   */
  const executeStream = useCallback(async (): Promise<{ success: boolean; error?: string }> => {
    // Validate model JSON if needed
    const validation = validateModelJson()
    if (!validation.valid) {
      setError({ message: validation.error! })
      return { success: false, error: validation.error }
    }

    // Clear previous state
    setLoading(true)
    setConnectionState('connecting')
    setError(null)
    setResult(null)
    setRawResponse(null)
    setStreamFrames([])

    const payload = buildPayload()
    const path = '/api/v1/chat/stream'

    try {
      const response = await fetch(`${API_BASE}${path}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'text/event-stream',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        let errorData: AgentError
        try {
          errorData = await response.json()
        } catch {
          errorData = { message: `${response.status} ${response.statusText}` }
        }

        setError(errorData)
        setConnectionState('error')
        setLoading(false)
        return { success: false, error: errorData.message }
      }

      const reader = response.body?.getReader()
      if (!reader) {
        setError({ message: 'Response body is not readable' })
        setConnectionState('error')
        setLoading(false)
        return { success: false, error: 'Response body is not readable' }
      }

      setConnectionState('connected')
      const frames: StreamFrame[] = []
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          break
        }

        buffer += decoder.decode(value, { stream: true })

        // Parse SSE frames (data: prefix)
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            try {
              const frame = JSON.parse(data) as StreamFrame
              frames.push(frame)

              // If this is a complete frame, parse the final result
              if (frame.type === 'complete') {
                const resultData = typeof frame.content === 'string'
                  ? JSON.parse(frame.content)
                  : frame.content

                setResult({
                  response: resultData.response || '',
                  conversationId: resultData.conversationId,
                  traceId: resultData.traceId,
                  data: resultData.data,
                })
              }
            } catch {
              // Skip unparseable frames
            }
          }
        }
      }

      setStreamFrames(frames)
      setConnectionState('connected')
      setLoading(false)
      return { success: true }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred'
      setError({ message: errorMessage })
      setConnectionState('error')
      setLoading(false)
      return { success: false, error: errorMessage }
    }
  }, [
    validateModelJson,
    buildPayload,
    setLoading,
    setConnectionState,
    setError,
    setResult,
    setRawResponse,
    setStreamFrames,
  ])

  return {
    executeSync,
    executeStream,
  }
}
