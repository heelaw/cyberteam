import { PlaygroundView } from '../../components/hybrid-pages'
import { createSeedState } from '../../lib/seed'

const seed = createSeedState()

export default function PlaygroundPage() {
  return <PlaygroundView seed={seed} />
}
