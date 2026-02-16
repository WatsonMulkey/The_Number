/// <reference types="vite/client" />

// Vue SFC module declarations for TypeScript strict mode
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<object, object, unknown>
  export default component
}
