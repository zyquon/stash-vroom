# JavaScript/TypeScript Package Implementation Plan

## Goal

Create a TypeScript package (`js/`) parallel to the Python package (`stash_vroom/`) that provides JAV and SLR file detection utilities. The package should be:

1. **npm-publishable** under the name `stash-vroom`
2. **Parallel to Python** in structure and test coverage
3. **Consumable by the plugin UI** via local file reference or npm

## Files to Create

### Package Configuration

| File | Purpose |
|------|---------|
| `js/package.json` | npm package config with exports, types, scripts |
| `js/tsconfig.json` | TypeScript compiler configuration |
| `js/vitest.config.ts` | Test runner configuration |
| `js/.gitignore` | Ignore dist/, node_modules/ |

### Source Files

| File | Purpose | Python Equivalent |
|------|---------|-------------------|
| `js/src/index.ts` | Public API re-exports | `stash_vroom/__init__.py` |
| `js/src/jav.ts` | JAV detection/parsing | `stash_vroom/jav.py` |
| `js/src/slr.ts` | SLR detection/parsing | `stash_vroom/slr.py` |
| `js/src/util.ts` | Video extension regex | `stash_vroom/util.py` |

### Test Files

| File | Purpose | Python Equivalent |
|------|---------|-------------------|
| `js/tests/jav.test.ts` | JAV parsing tests | `tests/tests_jav.py` |

## Implementation Details

### `jav.ts` - Core Logic

Port from `stash_vroom/jav.py`:

1. **`getJavInfo(filepath: string): JavInfo | null`**
   - Extract basename from path
   - Call `matchJavFilename()`
   - Filter year-based false positives (2010-2030)
   - Normalize `part` field (strip "part" prefix, uppercase)
   - Normalize `id` field (pad to 3 digits, trim excess leading zeros)
   - Return structured object or null

2. **`getIsJav(filepath: string): boolean`**
   - Convenience wrapper: `return getJavInfo(filepath) !== null`

3. **`matchJavFilename(filename: string): RegExpMatchArray | null`**
   - Check for SLR files (exclude)
   - Check for excluded suffixes/prefixes
   - Apply normalization regexes (~25 patterns):
     - Strip `.180.LR` suffixes
     - Handle Depth Anything output
     - Normalize WVR variants (WVR1, WVR6, WVR6D, WVR8, WVR9)
     - Normalize 3DSVR → DSVR
     - Strip video extensions, resolutions, MKX tags
   - Apply final JAV regex to capture groups

### `slr.ts` - SLR Detection

Port from `stash_vroom/slr.py`:

1. **`getSlrInfo(filepath: string): SlrInfo | null`**
   - Match against SLR filename pattern
   - Extract: site, studio, title, resolution, slrId, projection

2. **`getIsSlr(filepath: string): boolean`**
   - Convenience wrapper

3. **`getSlrRe(options?): string`**
   - Generate SLR matching regex

### `util.ts` - Shared Utilities

1. **`getVidRe(extensions?): string`**
   - Return regex pattern for video file extensions
   - Default: `['mp4', 'm4v', 'mkv', 'avi', 'webm', 'wmv', 'mov']`

### Type Definitions

```typescript
interface JavInfo {
  studio: string;   // e.g., "CBIKMV", "WVR6"
  id: string;       // e.g., "068", "001"
  mid: string;      // connector: "-", "_", " ", "", "."
  part: string;     // "A", "B", "1", "2", or ""
  filename: string; // original basename
}

interface SlrInfo {
  site: string;       // "SLR", "DeoVR", "JillVR"
  studio: string;     // studio name
  title: string;      // video title
  resolution: string; // "1080p", "original", etc.
  slrId: number;      // SLR database ID
  projection: string; // "LR_180", "TB_360", etc.
}
```

### Test Cases

Port all 30+ test cases from `tests/tests_jav.py`:

```typescript
const testCases: [string, ExpectedResult | null][] = [
  ['SkinRays_SunsetDance_180_LR.mp4', null],
  ['JillVR_1234.mp4', null],
  ['CBIKMV-068.24399-SLR.mp4', { studio: 'CBIKMV', mid: '-', id: '068', part: '' }],
  ['dandyhqvr-011-b.MP4', { studio: 'DANDYHQVR', mid: '-', id: '011', part: 'B' }],
  // ... all other cases
];
```

## Execution Order

1. Create `js/.gitignore`
2. Create `js/package.json`
3. Create `js/tsconfig.json`
4. Create `js/vitest.config.ts`
5. Create `js/src/util.ts`
6. Create `js/src/slr.ts`
7. Create `js/src/jav.ts`
8. Create `js/src/index.ts`
9. Create `js/tests/jav.test.ts`
10. Run `npm install` in `js/`
11. Run `npm test` to verify parity
12. Run `npm run build` to verify compilation

## Success Criteria

- [ ] All 30+ test cases pass
- [ ] `npm run build` produces `dist/` with `.js` and `.d.ts` files
- [ ] Package is importable: `import { getJavInfo } from 'stash-vroom'`
- [ ] Types work correctly in TypeScript projects
