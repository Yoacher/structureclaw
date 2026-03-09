import '@testing-library/jest-dom'

// Polyfills for Radix UI components in jsdom
// jsdom doesn't implement these DOM APIs that Radix UI uses

// Mock hasPointerCapture and releasePointerCapture
HTMLElement.prototype.hasPointerCapture = function (this: HTMLElement) {
  return false
}
HTMLElement.prototype.releasePointerCapture = function (this: HTMLElement) {}
HTMLElement.prototype.setPointerCapture = function (this: HTMLElement) {}

// Mock scrollIntoView
Element.prototype.scrollIntoView = function (this: Element) {}

// Mock getBoundingClientRect for Radix UI positioning
Element.prototype.getBoundingClientRect = function (this: Element) {
  return {
    width: 0,
    height: 0,
    top: 0,
    left: 0,
    bottom: 0,
    right: 0,
    x: 0,
    y: 0,
    toJSON: () => {},
  } as DOMRect
}

// Mock clientWidth and clientHeight for Radix UI
Object.defineProperties(HTMLElement.prototype, {
  clientWidth: {
    get() {
      return 0
    },
  },
  clientHeight: {
    get() {
      return 0
    },
  },
})

// Mock ResizeObserver for react-resizable-panels
class MockResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}
global.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver

// Mock EventSource for SSE hook testing
class MockEventSource {
  url: string
  readyState: number = EventSource.CONNECTING
  onopen: ((this: EventSource, ev: Event) => any) | null = null
  onmessage: ((this: EventSource, ev: MessageEvent) => any) | null = null
  onerror: ((this: EventSource, ev: Event) => any) | null = null

  constructor(url: string) {
    this.url = url
    // Simulate async connection establishment
    setTimeout(() => {
      this.readyState = EventSource.OPEN
      this.onopen?.call(this as unknown as EventSource, new Event('open'))
    }, 0)
  }

  close() {
    this.readyState = EventSource.CLOSED
  }

  addEventListener() {}
  removeEventListener() {}
}
global.EventSource = MockEventSource as unknown as typeof EventSource
