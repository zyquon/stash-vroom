/**
 * Utilities for working with JAV (Japanese Adult Video) files and filenames.
 *
 * @module jav
 */

import { basename, getVidRe } from './util.js';
import { getSlrInfo } from './slr.js';

/**
 * Metadata extracted from a JAV filename.
 */
export interface JavInfo {
  /** Studio/label code, e.g., "CBIKMV", "DANDYHQVR", "WVR6" */
  studio: string;
  /** Release ID, normalized (3+ digits, excess leading zeros trimmed) */
  id: string;
  /** The connector/separator found: "-", "_", " ", "", or "." */
  mid: string;
  /** Part identifier: "A", "B", "1", "2", etc., or empty string */
  part: string;
  /** Original filename (basename only) */
  filename: string;
}

/** Prefixes that indicate non-JAV content */
const EXCLUDED_PREFIXES = [
  'SLR-',
  'SLR_',
  'JillVR_',
  'realhotvr-',
  'wankzvr-',
  'reality-lovers-',
  'sexbabesvr-',
  'only2xvr-',
];

/** Years to exclude as false positives (e.g., "Title 2024") */
const EXCLUDED_YEARS = Array.from({ length: 20 }, (_, i) => String(2010 + i));

/**
 * Match a JAV filename pattern and return regex match groups.
 *
 * @param filename - The filename to match (basename only)
 * @returns Regex match array if matched, null otherwise
 */
export function matchJavFilename(filename: string): RegExpMatchArray | null {
  if (!filename || typeof filename !== 'string') {
    throw new Error(`Invalid filename: ${filename}`);
  }

  const okExtensionRe = getVidRe();

  // Check if it's an SLR file
  const slrInfo = getSlrInfo(filename);
  if (slrInfo) {
    return null;
  }

  // Check for excluded suffix
  if (filename.endsWith('-180_180x180_3dh_LR.mp4')) {
    return null;
  }

  // Check for excluded prefixes
  for (const prefix of EXCLUDED_PREFIXES) {
    if (filename.toLowerCase().startsWith(prefix.toLowerCase())) {
      return null;
    }
  }

  let fname = filename;

  // Strip .180.LR suffix
  fname = fname.replace(/\.180\.LR\b/gi, '');

  // Depth Anything output
  fname = fname.replace(/^scene-\d+\./i, '');
  fname = fname.replace(/\bdiv-\d+\.\d+ con-\d+\.\d+ fg-\d+\.\d+ ipd-\d+\b/gi, '');

  // Fix all the WVR variants first
  fname = fname.replace(/^WVR-10*?(\D)/i, 'WVR1$1');
  fname = fname.replace(/^WVR-1(\d)/i, 'WVR1$1');

  fname = fname.replace(/^WVR-11-(\d\d\d)/i, 'WVR1-$1');
  fname = fname.replace(/^WVR-2-(\d\d\d)/i, 'WVR1-$1');

  fname = fname.replace(/^WVR-101(\d\d\d)/i, 'WVR1$1');
  fname = fname.replace(/^WVR-11(\d\d\d)/i, 'WVR1$1');
  fname = fname.replace(/^WVR-2(\d)/i, 'WVR1$1');

  fname = fname.replace(/^WVR6D-/i, 'WVR6-');
  fname = fname.replace(/^WVR6-D(\d)/i, 'WVR6-$1');
  fname = fname.replace(/^WVR6D(\d\d\d)/i, 'WVR6$1');

  fname = fname.replace(/^WVR8(\d\d\w)\b/i, 'WVR80$1');
  fname = fname.replace(/^WVR-0*8/i, 'WVR8');

  fname = fname.replace(/^WVR-9(\d\d\d)/i, 'WVR9$1');
  fname = fname.replace(/^WVR9[cd]\b/i, 'WVR9');
  fname = fname.replace(/^WVR9[cd](\d)/i, 'WVR9$1');
  fname = fname.replace(/^WVR-91(\d\d\d)/i, 'WVR9$1');

  // Fix all the rest
  fname = fname.replace(/^3DSVR(\b|\d)/i, 'DSVR$1');

  fname = fname.replace(new RegExp(okExtensionRe, 'gi'), '');
  fname = fname.replace(/[-_\b]mkx199/gi, '');
  fname = fname.replace(/[-_\b]mkx219/gi, '');
  fname = fname.replace(/[-_]*(299|320|640|720|\d\d\d\d)p/gi, '');
  fname = fname.replace(/179-SBS\b/gi, '');
  fname = fname.replace(/179_LR\b/gi, '');
  fname = fname.replace(/_\d+-SLR\b/gi, ''); // SLR downloads

  const connectorRe = '[-_\\s\\.0]*?';
  const partRe = `(${connectorRe}|vrv18khia)` + '(\\d\\d?(?:\\b|_)|[a-z]\\b|part\\d+)';
  const javRe =
    '\\b' +
    '(WVR0|WVR1|WVR4|WVR8|WVR9|WVR6|[a-z]{3,9})' +
    `(${connectorRe})` +
    '(\\d{2,6})' +
    '(?:' +
    partRe +
    ')?';

  const match = fname.match(new RegExp(javRe, 'i'));
  return match;
}

/**
 * Extract JAV metadata from a filename or file path.
 *
 * @param filepath - A filename or file path
 * @returns JAV metadata if the file matches, null otherwise
 *
 * @example
 * ```ts
 * const info = getJavInfo('CBIKMV-068.24399-SLR.mp4');
 * // Returns: { studio: 'CBIKMV', id: '068', mid: '-', part: '', filename: 'CBIKMV-068.24399-SLR.mp4' }
 *
 * const info2 = getJavInfo('dandyhqvr-011-b.MP4');
 * // Returns: { studio: 'DANDYHQVR', id: '011', mid: '-', part: 'B', filename: 'dandyhqvr-011-b.MP4' }
 * ```
 */
export function getJavInfo(filepath: string): JavInfo | null {
  const filename = basename(filepath);
  const match = matchJavFilename(filename);

  if (!match) {
    return null;
  }

  // Filter out year-based false positives
  if (EXCLUDED_YEARS.includes(match[3])) {
    return null;
  }

  // Normalize part field
  let part = match[5] || '';
  part = part.replace(/^part/i, '');
  part = part.replace(/^(\d+)\D+$/, '$1'); // Remove trailing non-digits
  part = part.toUpperCase();

  // Normalize release ID (pad to 3 digits, trim excess leading zeros from 4+)
  let releaseId = String(match[3]);
  while (releaseId.length < 3) {
    releaseId = '0' + releaseId;
  }
  while (releaseId.length >= 4 && releaseId[0] === '0') {
    releaseId = releaseId.slice(1);
  }

  return {
    studio: match[1].toUpperCase(),
    id: releaseId,
    mid: match[2],
    part,
    filename,
  };
}

/**
 * Determine if the given file is a JAV (Japanese Adult Video) file.
 *
 * @param filepath - A filename or file path
 * @returns True if the file is a JAV, false otherwise
 *
 * @example
 * ```ts
 * getIsJav('CBIKMV-068.mp4'); // true
 * getIsJav('random-video.mp4'); // false
 * ```
 */
export function getIsJav(filepath: string): boolean {
  return getJavInfo(filepath) !== null;
}
