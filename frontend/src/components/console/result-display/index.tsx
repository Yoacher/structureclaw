import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card'
import { StatusHeader } from './status-header'
import { MetricsGrid } from './metrics-grid'
import { Timeline } from '../timeline'
import { ReportSummary } from '../report-summary'
import type { AgentResult } from '@/lib/stores/slices/console'

export interface ResultDisplayProps {
  result: AgentResult | null
}

/**
 * ResultDisplay is the main container that composes all result components
 */
export function ResultDisplay({ result }: ResultDisplayProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Execution Results</CardTitle>
        <CardDescription>
          Agent/Chat returned structured information
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <StatusHeader result={result} />

        {result?.response && (
          <p className="text-sm">{result.response}</p>
        )}

        {result?.clarification?.question && (
          <p className="text-sm text-yellow-600 dark:text-yellow-400">
            Clarification: {result.clarification.question}
          </p>
        )}

        {result?.metrics && (
          <MetricsGrid metrics={{
            toolCount: result.metrics.toolCount,
            failedToolCount: result.metrics.failedToolCount,
            totalToolDurationMs: result.metrics.totalToolDurationMs,
            maxToolDurationMs: result.metrics.maxToolDurationMs,
          }} />
        )}

        {result?.plan && result.plan.length > 0 && (
          <div>
            <h3 className="text-sm font-medium mb-2">Plan</h3>
            <ul className="list-disc list-inside text-sm space-y-1">
              {result.plan.map((item, idx) => (
                <li key={`plan-${idx}`}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        {result?.toolCalls && result.toolCalls.length > 0 && (
          <div>
            <h3 className="text-sm font-medium mb-2">Execution Timeline</h3>
            <Timeline calls={result.toolCalls.map(call => ({
              tool: call.name || 'unknown',
              status: call.result ? 'success' : 'error',
              durationMs: 0,
            }))} />
          </div>
        )}

        {result?.artifacts && result.artifacts.length > 0 && (
          <div>
            <h3 className="text-sm font-medium mb-2">Artifacts</h3>
            <ul className="list-disc list-inside text-sm space-y-1">
              {result.artifacts.map((artifact, idx) => (
                <li key={`artifact-${idx}`}>
                  {artifact.format}: {artifact.path}
                </li>
              ))}
            </ul>
          </div>
        )}

        {result?.data?.report && (
          <ReportSummary report={result.data.report as { summary?: string; markdown?: string }} />
        )}
      </CardContent>
    </Card>
  )
}

export { StatusHeader } from './status-header'
export { MetricsGrid } from './metrics-grid'
