// Store context and provider
export {
  AppStoreProvider,
  AppStoreContext,
  useStore,
  createAppStore,
  initStore,
  type StoreState,
  type AppStoreProviderProps,
} from './context'

// Console slice
export {
  createConsoleSlice,
  initialConsoleState,
  type ConsoleState,
  type ConsoleActions,
  type ConsoleSlice,
} from './slices/console'
