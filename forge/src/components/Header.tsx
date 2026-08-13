import { useState } from 'react'
import { Link, NavLink } from 'react-router'
import Wordmark from './Wordmark'

const nav = [
  { to: '/agents', label: 'Agents' },
  { to: '/workflows', label: 'Workflows' },
  { to: '/install', label: 'Install' },
  { to: '/compatibility', label: 'Compatibility' },
]

export default function Header() {
  const [open, setOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 border-b border-border/80 bg-background/85 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-[1280px] items-center justify-between gap-4 px-5 sm:px-8">
        <Wordmark onClick={() => setOpen(false)} />

        <nav className="hidden items-center gap-1 md:flex" aria-label="Primary">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `rounded-lg px-3 py-2 text-[14px] font-medium transition-colors ${
                  isActive
                    ? 'text-primary'
                    : 'text-muted-foreground hover:text-foreground'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <Link
            to="/install"
            className="hidden rounded-xl bg-primary px-4 py-2.5 text-[14px] font-semibold text-primary-foreground shadow-[0_2px_8px_rgba(18,86,74,0.22)] transition-colors hover:bg-primary-hover sm:inline-flex"
          >
            Install 172X
          </Link>

          <button
            type="button"
            className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-border-strong text-foreground md:hidden"
            aria-label={open ? 'Close menu' : 'Open menu'}
            aria-expanded={open}
            onClick={() => setOpen((v) => !v)}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden>
              {open ? (
                <path
                  d="m6 6 12 12M18 6 6 18"
                  stroke="currentColor"
                  strokeWidth="1.7"
                  strokeLinecap="round"
                />
              ) : (
                <path
                  d="M4 7h16M4 12h16M4 17h16"
                  stroke="currentColor"
                  strokeWidth="1.7"
                  strokeLinecap="round"
                />
              )}
            </svg>
          </button>
        </div>
      </div>

      {open && (
        <div className="border-t border-border bg-background md:hidden">
          <nav
            className="mx-auto flex max-w-[1280px] flex-col gap-1 px-5 py-4"
            aria-label="Mobile"
          >
            {nav.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setOpen(false)}
                className={({ isActive }) =>
                  `rounded-lg px-3 py-2.5 text-[15px] font-medium transition-colors ${
                    isActive
                      ? 'bg-primary/8 text-primary'
                      : 'text-foreground hover:bg-muted'
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
            <Link
              to="/install"
              onClick={() => setOpen(false)}
              className="mt-2 rounded-xl bg-primary px-4 py-3 text-center text-[15px] font-semibold text-primary-foreground"
            >
              Install 172X
            </Link>
          </nav>
        </div>
      )}
    </header>
  )
}
