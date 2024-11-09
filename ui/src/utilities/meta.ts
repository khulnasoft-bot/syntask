export function BASE_URL(): string | undefined {
  return import.meta.env.BASE_URL
}

export function MODE(): string {
  return import.meta.env.MODE
}

export function VITE_SYNTASK_CANARY(): boolean {
  return import.meta.env.VITE_SYNTASK_CANARY === 'true'
}