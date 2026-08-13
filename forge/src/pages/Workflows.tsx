import { Container, PageHeading } from '../components/Container'
import Breadcrumb from '../components/Breadcrumb'
import WorkflowCard from '../components/WorkflowCard'
import { workflows } from '../data/workflows'

export default function Workflows() {
  return (
    <Container className="py-10">
      <Breadcrumb items={[{ label: 'Forge', to: '/' }, { label: 'Workflows' }]} />
      <div className="mt-5">
        <PageHeading
          eyebrow="Orchestration"
          title="Workflows"
          description="Composable sequences that coordinate specialists toward an outcome. Workflows guide host-coordinated work — they are not a separate execution engine."
        />
      </div>

      <div className="mt-9 grid gap-4 lg:grid-cols-2">
        {workflows.map((w) => (
          <WorkflowCard key={w.slug} workflow={w} />
        ))}
      </div>
    </Container>
  )
}
