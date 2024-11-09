import { showToast } from '@synopkg/synotask-design'

export function copyToClipboard(text: string, message: string = 'Copied to clipboard!'): void {
  navigator.clipboard.writeText(text)

  showToast(message, 'success')
}