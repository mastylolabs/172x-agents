import { Container, PageHeading } from '../components/Container'
import Breadcrumb from '../components/Breadcrumb'
import { compatibility } from '../data/compatibility'

export default function Compatibility() {
  return (
    <Container className="py-10">
      <Breadcrumb
        items={[{ label: 'Forge', to: '/' }, { label: 'Compatibility' }]}
      />
      <div className="mt-5">
        <PageHeading
          eyebrow="Support matrix"
          title="Compatibility"
          description="What Forge supports today, and what is planned. We list only what actually works — no exaggerated claims."
        />
      </div>

      <div className="mt-8 flex flex-wrap gap-4 text-[13px]">
        <span className="inline-flex items-center gap-2 text-muted-foreground">
          <span className="h-2.5 w-2.5 rounded-full bg-primary" /> Supported now
        </span>
        <span className="inline-flex items-center gap-2 text-muted-foreground">
          <span className="h-2.5 w-2.5 rounded-full border border-accent/50 bg-accent-soft" />
          Planned
        </span>
      </div>

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        {compatibility.map((group) => (
          <div
            key={group.category}
            className="rounded-[16px] border border-border bg-card p-5"
          >
            <h2 className="font-display text-[16px] font-bold tracking-tight text-foreground">
              {group.category}
            </h2>
            <ul className="mt-4 divide-y divide-border">
              {group.items.map((item) => {
                const supported = item.status === 'supported'
                return (
                  <li
                    key={item.name}
                    className="flex items-center justify-between py-2.5"
                  >
                    <span className="flex items-center gap-2.5">
                      <span
                        aria-hidden
                        className={`h-2.5 w-2.5 rounded-full ${
                          supported
                            ? 'bg-primary'
                            : 'border border-accent/50 bg-accent-soft'
                        }`}
                      />
                      <span className="text-[15px] font-medium text-foreground">
                        {item.name}
                      </span>
                    </span>
                    <span
                      className={`text-[13px] font-medium ${
                        supported ? 'text-primary' : 'text-muted-foreground'
                      }`}
                    >
                      {supported ? 'Supported' : 'Planned'}
                    </span>
                  </li>
                )
              })}
            </ul>
          </div>
        ))}
      </div>

      <p className="mt-8 max-w-2xl text-[14px] leading-relaxed text-muted-foreground">
        Planned support is under active consideration and not yet available.
        Commands and installs assume the currently supported profile: Codex,
        Python, Git, GitHub, and macOS.
      </p>
    </Container>
  )
}
