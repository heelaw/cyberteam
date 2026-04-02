import { SettingsView } from '../../components/hybrid-pages'
import { createSeedState } from '../../lib/seed'

const seed = createSeedState()

export default function SettingsPage() {
  return <SettingsView seed={seed} />
}
