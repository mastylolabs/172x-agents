import { NavLink } from 'react-router'
import { domains } from '../data/domains'
import { domainIcon } from './Icons'

export default function DomainTabs() {
  return (
    <div className="flex gap-2 overflow-x-auto pb-1 no-scrollbar">
      <TabLink to="/agents" label="All" exact />
      {domains.map((d) => {
        const Icon = domainIcon[d.slug]
        return (
          <TabLink
            key={d.slug}
            to={`/agents/${d.slug}`}
            label={d.name}
            icon={<Icon width={16} height={16} />}
          />
        )
      })}
    </div>
  )
}

function TabLink({
  to,
  label,
  icon,
  exact = false,
}: {
  to: string
  label: string
  icon?: React.ReactNode
  exact?: boolean
}) {
  return (
    <NavLink
      to={to}
      end={exact}
      className={({ isActive }) =>
        `inline-flex shrink-0 items-center gap-2 rounded-full border px-4 py-2 text-[14px] font-medium transition-colors ${
          isActive
            ? 'border-primary bg-primary text-primary-foreground shadow-[0_2px_8px_rgba(18,86,74,0.2)]'
            : 'border-border-strong bg-card text-muted-foreground hover:border-primary/30 hover:text-primary'
        }`
      }
    >
      {icon}
      {label}
    </NavLink>
  )
}
