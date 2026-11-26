// Generic freshness probe for launcher.bat.
//
// Answers one question: is DIST_MARKER older than any source/config file?
// Prints exactly "fresh" or "stale" on stdout and ALWAYS exits 0, so a
// shell can branch on stdout rather than the exit code ("needs rebuild"
// is not an error). A missing marker is simply "stale".
//
// Usage:
//   node needs-build.mjs <marker> <path> [<path> ...]
//
// Paths may be files or directories. Directories are walked recursively;
// node_modules and any dot-directory (.backup, .trash, .cache,
// .svelte-kit, ...) are skipped because their mtimes change constantly
// and say nothing about your sources.

import { existsSync, statSync, readdirSync } from 'node:fs';
import { resolve, join, basename } from 'node:path';

const args = process.argv.slice(2);
if (args.length < 2) {
  console.error('usage: node needs-build.mjs <marker> <path> [<path> ...]');
  process.exit(0); // still exit 0: the launcher treats non-"fresh" as stale
}

const [markerArg, ...sourceArgs] = args;
const marker = resolve(markerArg);

// When the marker does not exist there is nothing fresh to speak of.
if (!existsSync(marker)) {
  console.log('stale');
  process.exit(0);
}
const markerMtime = statSync(marker).mtimeMs;

const SKIP_DIRS = new Set(['node_modules']);

function shouldSkip(name) {
  if (SKIP_DIRS.has(name)) return true;
  if (name.startsWith('.')) return true; // .backup / .trash / .cache / ...
  return false;
}

function newestMtime(p, seen = new Set()) {
  let newest = 0;
  const st = statSync(p);
  if (st.isDirectory()) {
    // Guard against symlink loops.
    const real = statSync(p).ino;
    if (seen.has(real)) return 0;
    seen.add(real);
    for (const entry of readdirSync(p)) {
      if (shouldSkip(entry)) continue;
      newest = Math.max(newest, newestMtime(join(p, entry), seen));
      if (newest > markerMtime) return newest; // early out: already stale
    }
  } else {
    newest = st.mtimeMs;
  }
  return newest;
}

let newest = 0;
for (const src of sourceArgs) {
  const p = resolve(src);
  if (!existsSync(p)) continue;
  newest = Math.max(newest, newestMtime(p, new Set()));
  if (newest > markerMtime) {
    console.log('stale');
    process.exit(0);
  }
}

console.log(newest > markerMtime ? 'stale' : 'fresh');
process.exit(0);