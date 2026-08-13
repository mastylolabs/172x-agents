import { Link } from 'react-router'
import { Container } from '../components/Container'

export default function NotFound() {
  return (
    <Container className="py-24 text-center">
      <div className="font-mono text-[13px] uppercase tracking-[0.16em] text-accent">
        404
      </div>
      <h1 className="mt-3 font-display text-[clamp(1.8rem,4vw,2.5rem)] font-extrabold tracking-tight text-foreground">
        This page hasn’t been forged.
      </h1>
      <p className="mx-auto mt-3 max-w-md text-[15px] leading-relaxed text-muted-foreground">
        The specialist or workflow you’re looking for doesn’t exist yet. Browse
        the library to find what you need.
      </p>
      <div className="mt-7 flex flex-wrap justify-center gap-3">
        <Link
          to="/agents"
          className="rounded-xl bg-primary px-5 py-3 text-[15px] font-semibold text-primary-foreground transition-colors hover:bg-primary-hover"
        >
          Browse agents
        </Link>
        <Link
          to="/"
          className="rounded-xl border border-border-strong bg-card px-5 py-3 text-[15px] font-semibold text-foreground transition-colors hover:border-primary/30 hover:text-primary"
        >
          Back to Forge
        </Link>
      </div>
    </Container>
  )
}
