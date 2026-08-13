import { Link } from 'react-router'
import Wordmark from './Wordmark'
import { domains } from '../data/domains'

export default function Footer() {
  return (
    <footer className="mt-24 border-t border-border bg-card/60">
      <div className="mx-auto max-w-[1280px] px-5 py-14 sm:px-8">
        <div className="grid gap-10 md:grid-cols-[1.4fr_1fr_1fr_1fr]">
          <div>
            <Wordmark />
            <p className="mt-4 max-w-xs text-[14px] leading-relaxed text-muted-foreground">
              A curated, open-source library of composable AI-agent specialists
              and workflows for serious builders.
            </p>
            <p className="mt-4 font-mono text-[12px] text-muted-foreground">
              forge.172x.ai
            </p>
          </div>

          <FooterCol title="Browse">
            <FooterLink to="/agents">All agents</FooterLink>
            <FooterLink to="/workflows">Workflows</FooterLink>
            <FooterLink to="/install">Install</FooterLink>
            <FooterLink to="/compatibility">Compatibility</FooterLink>
          </FooterCol>

          <FooterCol title="Domains">
            {domains.map((d) => (
              <FooterLink key={d.slug} to={`/agents/${d.slug}`}>
                {d.name}
              </FooterLink>
            ))}
          </FooterCol>

          <FooterCol title="Getting started">
            <FooterLink to="/install">Command builder</FooterLink>
            <FooterLink to="/workflows/dev-loop">Dev Loop</FooterLink>
            <FooterLink to="/agents/principal-architect">
              Principal Architect
            </FooterLink>
          </FooterCol>
        </div>

        <div className="mt-12 flex flex-col items-start justify-between gap-3 border-t border-border pt-6 text-[13px] text-muted-foreground sm:flex-row sm:items-center">
          <p>
            © 2026{' '}
            <a
              href="https://mastylolabs.com"
              className="transition-colors hover:text-primary"
            >
              Mastylo Labs LLC
            </a>
          </p>
          <p className="font-mono text-[12px]">
            Supported now: Codex · Python · Git · GitHub · macOS
          </p>
        </div>
      </div>
    </footer>
  )
}

function FooterCol({
  title,
  children,
}: {
  title: string
  children: React.ReactNode
}) {
  return (
    <div>
      <h4 className="text-[12px] font-semibold uppercase tracking-[0.12em] text-foreground/70">
        {title}
      </h4>
      <ul className="mt-3 space-y-2">{children}</ul>
    </div>
  )
}

function FooterLink({ to, children }: { to: string; children: React.ReactNode }) {
  return (
    <li>
      <Link
        to={to}
        className="text-[14px] text-muted-foreground transition-colors hover:text-primary"
      >
        {children}
      </Link>
    </li>
  )
}
