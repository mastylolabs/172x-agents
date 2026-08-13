import { Link } from 'react-router'

export default function Wordmark({ onClick }: { onClick?: () => void }) {
  return (
    <Link
      to="/"
      onClick={onClick}
      className="group inline-flex items-center gap-2.5"
      aria-label="172X Forge home"
    >
      <span className="relative inline-flex h-8 w-8 items-center justify-center rounded-[9px] bg-primary text-primary-foreground shadow-[0_2px_6px_rgba(18,86,74,0.28)]">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
          <path
            d="M12 2.5 4 6.5v6l8 4 8-4v-6l-8-4Z"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinejoin="round"
          />
          <path
            d="m8.5 10.5 3 1.5 3-1.5"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
        <span className="absolute -bottom-0.5 -right-0.5 h-2 w-2 rounded-full border-2 border-background bg-accent" />
      </span>
      <span className="font-display text-[17px] font-extrabold tracking-tight text-foreground">
        172X <span className="text-primary">Forge</span>
      </span>
    </Link>
  )
}
