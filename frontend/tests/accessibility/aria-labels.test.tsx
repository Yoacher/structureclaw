import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ErrorDisplay } from '@/components/console/error-display'
import { ClarificationPrompt } from '@/components/console/clarification-prompt'
import type { AgentError, Clarification } from '@/lib/api/contracts/agent'

/**
 * ARIA Labels Tests (ACCS-04)
 *
 * These tests verify that all interactive elements have proper accessible names:
 * - Icon-only buttons have aria-label
 * - Form inputs have accessible names (via label or aria-label)
 * - Dynamic content has aria-live attributes
 * - Error messages have role="alert"
 */
describe('ARIA Labels (ACCS-04)', () => {
  const user = userEvent.setup()

  beforeEach(() => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('ErrorDisplay', () => {
    it('has role="alert"', () => {
      const error: AgentError = { message: 'Test error' }
      render(<ErrorDisplay error={error} />)
      expect(screen.getByRole('alert')).toBeInTheDocument()
    })

    it('error message is announced to screen readers', () => {
      const error: AgentError = { message: 'Test error message' }
      render(<ErrorDisplay error={error} />)
      const alert = screen.getByRole('alert')
      expect(alert).toHaveTextContent('Test error message')
    })

    it('decorative icon has aria-hidden="true"', () => {
      const error: AgentError = { message: 'Test error' }
      render(<ErrorDisplay error={error} />)
      const icon = screen.getByRole('alert').querySelector('svg')
      expect(icon).toHaveAttribute('aria-hidden', 'true')
    })

    it('error code is displayed when provided', () => {
      const error: AgentError = { message: 'Test error', code: 'ERR_001' }
      render(<ErrorDisplay error={error} />)
      expect(screen.getByText(/ERR_001/)).toBeInTheDocument()
    })
  })

  describe('ClarificationPrompt', () => {
    it('has accessible label via aria-label', () => {
      const clarification: Clarification = { question: 'Need info?' }
      render(<ClarificationPrompt clarification={clarification} />)
      expect(screen.getByLabelText(/clarification needed/i)).toBeInTheDocument()
    })

    it('question is accessible to screen readers', () => {
      const clarification: Clarification = { question: 'What is needed?' }
      render(<ClarificationPrompt clarification={clarification} />)
      const prompt = screen.getByLabelText(/clarification needed/i)
      expect(prompt).toHaveTextContent('What is needed?')
    })

    it('decorative icon has aria-hidden="true"', () => {
      const clarification: Clarification = { question: 'Need info?' }
      render(<ClarificationPrompt clarification={clarification} />)
      const icon = screen.getByLabelText(/clarification needed/i).querySelector('svg')
      expect(icon).toHaveAttribute('aria-hidden', 'true')
    })

    it('missing fields are accessible', () => {
      const clarification: Clarification = {
        question: 'Missing info?',
        missingFields: ['field1', 'field2'],
      }
      render(<ClarificationPrompt clarification={clarification} />)
      const prompt = screen.getByLabelText(/clarification needed/i)
      expect(prompt).toHaveTextContent('field1')
      expect(prompt).toHaveTextContent('field2')
    })
  })

  describe('Dynamic content', () => {
    it('error display has aria-live="assertive"', () => {
      const error: AgentError = { message: 'Error' }
      render(<ErrorDisplay error={error} />)
      const alert = screen.getByRole('alert')
      expect(alert).toHaveAttribute('aria-live', 'assertive')
    })

    it('clarification prompt has aria-live="polite"', () => {
      const clarification: Clarification = { question: 'Question?' }
      render(<ClarificationPrompt clarification={clarification} />)
      const prompt = screen.getByLabelText(/clarification needed/i)
      expect(prompt).toHaveAttribute('aria-live', 'polite')
    })
  })

  describe('Semantic structure', () => {
    it('ErrorDisplay uses semantic HTML elements', () => {
      const error: AgentError = { message: 'Test error' }
      render(<ErrorDisplay error={error} />)
      const alert = screen.getByRole('alert')
      // Should contain semantic p elements
      expect(alert.querySelector('p')).toBeInTheDocument()
    })

    it('ClarificationPrompt uses semantic HTML elements', () => {
      const clarification: Clarification = {
        question: 'Question?',
        missingFields: ['field1'],
      }
      render(<ClarificationPrompt clarification={clarification} />)
      const prompt = screen.getByLabelText(/clarification needed/i)
      // Should contain semantic elements
      expect(prompt.querySelector('p')).toBeInTheDocument()
      expect(prompt.querySelector('ul')).toBeInTheDocument()
      expect(prompt.querySelector('li')).toBeInTheDocument()
    })

    it('ClarificationPrompt has role="region"', () => {
      const clarification: Clarification = { question: 'Question?' }
      render(<ClarificationPrompt clarification={clarification} />)
      const prompt = screen.getByLabelText(/clarification needed/i)
      expect(prompt).toHaveAttribute('role', 'region')
    })
  })

  describe('Accessible names', () => {
    it('ErrorDisplay title has descriptive text', () => {
      const error: AgentError = { message: 'Test error' }
      render(<ErrorDisplay error={error} />)
      expect(screen.getByText('Error')).toBeInTheDocument()
    })

    it('ClarificationPrompt title has descriptive text', () => {
      const clarification: Clarification = { question: 'Question?' }
      render(<ClarificationPrompt clarification={clarification} />)
      expect(screen.getByText('Clarification Required')).toBeInTheDocument()
    })

    it('missing fields section has descriptive label', () => {
      const clarification: Clarification = {
        question: 'Question?',
        missingFields: ['field1'],
      }
      render(<ClarificationPrompt clarification={clarification} />)
      expect(screen.getByText('Missing Fields')).toBeInTheDocument()
    })
  })
})
