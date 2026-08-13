import { useState } from 'react'
import { CopyIcon, CheckIcon } from './Icons'

export default function CommandBlock({
  command,
  label,
  compact = false,
}: {
  command: string
  label?: string
  compact?: boolean
}) {
  const [copied, setCopied] = useState(false)

  const copy = async () => {
    try {
      let copied = false
      if (navigator.clipboard && window.isSecureContext) {
        try {
          await navigator.clipboard.writeText(command)
          copied = true
        } catch {
          copied = false
        }
      }
      if (!copied) copied = copyWithSelection(command)
      if (!copied) {
        throw new Error('Clipboard access is unavailable')
      }
      setCopied(true)
      setTimeout(() => setCopied(false), 1600)
    } catch {
      setCopied(false)
    }
  }

  return (
    <div className="group">
      {label && (
        <div className="mb-1.5 text-[11px] font-medium uppercase tracking-[0.12em] text-muted-foreground">
          {label}
        </div>
      )}
      <div
        className={`flex items-center gap-3 rounded-xl border border-border-strong bg-foreground/[0.03] ${
          compact ? 'px-3 py-2' : 'px-4 py-3'
        }`}
      >
        <span aria-hidden className="select-none font-mono text-sm text-accent">
          $
        </span>
        <code className="min-w-0 flex-1 break-words whitespace-pre-wrap font-mono text-[13px] text-foreground">
          {command}
        </code>
        <button
          type="button"
          onClick={copy}
          aria-label={copied ? 'Copied to clipboard' : 'Copy command'}
          className="inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-border-strong bg-card px-2.5 py-1.5 text-[12px] font-medium text-muted-foreground transition-colors hover:border-primary/40 hover:text-primary"
        >
          {copied ? (
            <>
              <CheckIcon width={14} height={14} /> Copied
            </>
          ) : (
            <>
              <CopyIcon width={14} height={14} /> Copy
            </>
          )}
        </button>
      </div>
    </div>
  )
}

function copyWithSelection(value: string): boolean {
  const textarea = document.createElement('textarea')
  textarea.value = value
  textarea.setAttribute('readonly', '')
  textarea.style.cssText = 'position:fixed;opacity:0;pointer-events:none'
  document.body.append(textarea)
  textarea.select()
  const copied = document.execCommand('copy')
  textarea.remove()
  return copied
}
