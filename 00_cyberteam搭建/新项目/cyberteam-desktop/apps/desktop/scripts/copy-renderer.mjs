import { mkdir, cp, rm } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const scriptDir = path.dirname(fileURLToPath(import.meta.url))
const desktopRoot = path.resolve(scriptDir, '..')
const rendererOut = path.resolve(desktopRoot, '..', 'renderer', 'out')
const targetDir = path.resolve(desktopRoot, 'dist', 'renderer', 'out')

async function main() {
  await rm(path.resolve(desktopRoot, 'dist', 'renderer'), { recursive: true, force: true })
  await mkdir(path.dirname(targetDir), { recursive: true })
  await cp(rendererOut, targetDir, { recursive: true })
  console.log(`[copy-renderer] ${rendererOut} -> ${targetDir}`)
}

main().catch((error) => {
  console.error('[copy-renderer] failed:', error)
  process.exitCode = 1
})
