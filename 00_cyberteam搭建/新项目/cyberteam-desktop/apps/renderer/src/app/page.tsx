import { DashboardView } from '../components/hybrid-pages'
import { createSeedState } from '../lib/seed'

const seed = createSeedState()

export default function HomePage() {
  return <DashboardView seed={seed} />
}
