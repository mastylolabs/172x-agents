import { createBrowserRouter } from 'react-router'
import AppShell from './components/AppShell'
import Home from './pages/Home'
import AgentsIndex from './pages/AgentsIndex'
import AgentRoute from './pages/AgentRoute'
import Workflows from './pages/Workflows'
import WorkflowDetail from './pages/WorkflowDetail'
import Install from './pages/Install'
import Compatibility from './pages/Compatibility'
import NotFound from './pages/NotFound'

export const router = createBrowserRouter([
  {
    path: '/',
    Component: AppShell,
    children: [
      { index: true, Component: Home },
      { path: 'agents', Component: AgentsIndex },
      { path: 'agents/:slug', Component: AgentRoute },
      { path: 'workflows', Component: Workflows },
      { path: 'workflows/:slug', Component: WorkflowDetail },
      { path: 'install', Component: Install },
      { path: 'compatibility', Component: Compatibility },
      { path: '*', Component: NotFound },
    ],
  },
])
