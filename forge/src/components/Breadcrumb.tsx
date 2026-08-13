import { Link } from 'react-router'

export interface Crumb {
  label: string
  to?: string
}

export default function Breadcrumb({ items }: { items: Crumb[] }) {
  return (
    <nav aria-label="Breadcrumb">
      <ol className="flex flex-wrap items-center gap-1.5 text-[13px] text-muted-foreground">
        {items.map((item, i) => (
          <li key={item.label} className="flex items-center gap-1.5">
            {item.to ? (
              <Link
                to={item.to}
                className="transition-colors hover:text-primary"
              >
                {item.label}
              </Link>
            ) : (
              <span className="text-foreground">{item.label}</span>
            )}
            {i < items.length - 1 && (
              <span aria-hidden className="text-border-strong">
                /
              </span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  )
}
