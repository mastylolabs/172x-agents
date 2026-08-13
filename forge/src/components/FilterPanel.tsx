export default function FilterPanel({
  options,
  active,
  onChange,
}: {
  options: string[]
  active: string
  onChange: (v: string) => void
}) {
  return (
    <div
      role="group"
      aria-label="Filter"
      className="flex gap-2 overflow-x-auto pb-1 no-scrollbar"
    >
      {options.map((option) => {
        const selected = option === active
        return (
          <button
            key={option}
            type="button"
            aria-pressed={selected}
            onClick={() => onChange(option)}
            className={`shrink-0 rounded-full border px-3.5 py-1.5 text-[13px] font-medium transition-colors ${
              selected
                ? 'border-accent/40 bg-accent-soft text-accent-foreground'
                : 'border-border-strong bg-card text-muted-foreground hover:border-primary/30 hover:text-primary'
            }`}
          >
            {option}
          </button>
        )
      })}
    </div>
  )
}
