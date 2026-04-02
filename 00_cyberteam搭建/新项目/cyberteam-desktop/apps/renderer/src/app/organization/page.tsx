import { OrganizationView } from '../../components/hybrid-pages'
import { createSeedState } from '../../lib/seed'

const seed = createSeedState()

export default function OrganizationPage() {
  return <OrganizationView seed={seed} />
}
