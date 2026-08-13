import { Link } from 'react-router'
import type { Workflow } from '../data/types'
import { ArrowIcon } from './Icons'

export default function WorkflowCard({ workflow }: { workflow: Workflow }) {
  return (
    <Link
      to={`/workflows/${workflow.slug}`}
      className="group flex h-full flex-col rounded-[16px] border border-border bg-card p-6 shadow-[0_1px_2px_rgba(27,35,32,0.04)] transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-[0_8px_24px_rgba(18,86,74,0.08)]"
    >
      <div className="flex items-center justify-between">
        <span className="font-mono text-[11px] uppercase tracking-[0.14em] text-accent">
          Workflow
        </span>
        <span className="font-mono text-[11px] text-muted-foreground">
          v{workflow.version}
        </span>
      </div>

      <h3 className="mt-3 font-display text-[20px] font-bold tracking-tight text-foreground">
        {workflow.name}
      </h3>
      <p className="mt-2 text-[14px] leading-relaxed text-muted-foreground">
        {workflow.outcome}
      </p>

      <div className="mt-5 flex flex-wrap items-center gap-x-1.5 gap-y-2">
        {workflow.steps.map((step, i) => (
          <span key={step} className="flex items-center gap-1.5">
            <span className="rounded-md border border-border bg-muted/70 px-2 py-1 text-[11px] font-medium text-foreground/80">
              {step}
            </span>
            {i < workflow.steps.length - 1 && (
              <span aria-hidden className="text-border-strong">
                →
              </span>
            )}
          </span>
        ))}
      </div>

      <div className="mt-auto flex items-center gap-1.5 pt-6 text-[13px] font-semibold text-primary">
        View workflow
        <ArrowIcon
          width={15}
          height={15}
          className="transition-transform duration-200 group-hover:translate-x-0.5"
        />
      </div>
    </Link>
  )
}
