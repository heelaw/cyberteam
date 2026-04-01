import { MarketView } from '../../components/hybrid-pages'
import { createSeedState } from '../../lib/seed'

const seed = createSeedState()

export default function MarketPage() {
  return <MarketView seed={seed} />
}
