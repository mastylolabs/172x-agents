import { SearchIcon } from './Icons'

export default function SearchBar({
  value,
  onChange,
  placeholder = 'Search agents, workflows, or outcomes…',
  size = 'lg',
  autoFocus = false,
}: {
  value: string
  onChange: (v: string) => void
  placeholder?: string
  size?: 'lg' | 'md'
  autoFocus?: boolean
}) {
  const large = size === 'lg'
  return (
    <div className="relative">
      <SearchIcon
        aria-hidden
        className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground"
        width={large ? 22 : 18}
        height={large ? 22 : 18}
      />
      <input
        type="search"
        value={value}
        autoFocus={autoFocus}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        aria-label={placeholder}
        className={`w-full rounded-2xl border border-border-strong bg-card text-foreground shadow-[0_1px_0_rgba(0,0,0,0.02)] transition-colors placeholder:text-muted-foreground/80 hover:border-primary/30 focus:border-primary focus:outline-none ${
          large ? 'py-4 pr-4 text-[17px]' : 'py-2.5 pr-3.5 text-[15px]'
        }`}
        style={large ? { paddingLeft: '3.25rem' } : { paddingLeft: '2.75rem' }}
      />
    </div>
  )
}
