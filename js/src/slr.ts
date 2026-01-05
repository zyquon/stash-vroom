/**
 * Utilities for working with files downloaded from SLR and its network.
 *
 * Helps to detect and extract important information from SLR download filenames.
 *
 * @module slr
 */

import { basename } from './util.js';

/**
 * Metadata extracted from an SLR-style filename.
 */
export interface SlrInfo {
  /** The site name: "SLR", "DeoVR", or "JillVR" */
  site: string;
  /** The studio name */
  studio: string;
  /** The video title */
  title: string;
  /** Video resolution: "1080p", "2160p", "original", etc. */
  resolution: string;
  /** SLR database ID */
  slrId: number;
  /** Projection format: "LR_180", "TB_360", "FISHEYE190", etc. */
  projection: string;
}

export interface SlrReOptions {
  /** Prefix for the regex: "^" for filenames, "/" for file paths */
  prefix?: '^' | '/';
  /** Site pattern to match */
  site?: string;
  /** Studio pattern to match */
  studio?: string;
  /** If true, generates shorter regex without resolution/projection */
  short?: boolean;
}

/**
 * Generate a regular expression to match SLR-style filenames.
 *
 * @param options - Options for customizing the regex
 * @returns A regex pattern string
 *
 * @example
 * ```ts
 * const pattern = getSlrRe();
 * // Matches: SLR_StudioName_Title_1080p_12345_LR_180.mp4
 * ```
 */
export function getSlrRe(options: SlrReOptions = {}): string {
  const { prefix = '^', site = 'SLR|DeoVR|JillVR', studio: studioOpt, short = false } = options;

  let rePrefix: string;
  if (prefix === '^') {
    rePrefix = '^';
  } else if (prefix === '/') {
    rePrefix = '^/.+/';
  } else {
    throw new Error('Prefix must be "^" or "/"');
  }

  const studio = studioOpt || '.+?';

  let result = rePrefix + '(' + site + ')_(' + studio + ')_(.+)';
  if (!short) {
    result += '_(original|\\d+p)_(\\d+)_(LR_180|TB_360|FISHEYE190_alpha|FISHEYE190|FISHEYE|MKX200)';
  }
  result += '(\\.fix|\\.mp4)?\\.mp4$';

  return result;
}

/**
 * Extract metadata from SLR-style filenames.
 *
 * @param filepath - A filename or file path
 * @returns Metadata object if the file matches SLR pattern, null otherwise
 *
 * @example
 * ```ts
 * const info = getSlrInfo('SLR_StudioName_Title_Original_1080p_12345_LR_180.mp4');
 * // Returns: { site: 'SLR', studio: 'StudioName', title: 'Title_Original', ... }
 * ```
 */
export function getSlrInfo(filepath: string): SlrInfo | null {
  const filename = basename(filepath);

  const studioRe = getSlrRe();
  const match = filename.match(new RegExp(studioRe, 'i'));

  if (!match) {
    return null;
  }

  let projection = match[6];
  if (projection === 'FISHEYE190_alpha') {
    projection = 'FISHEYE190';
  }

  return {
    site: match[1],
    studio: match[2],
    title: match[3],
    resolution: match[4],
    slrId: parseInt(match[5], 10),
    projection,
  };
}

/**
 * Determine if the given file is an SLR or related site download.
 *
 * @param filepath - A filename or file path
 * @returns True if the file is an SLR download, false otherwise
 *
 * @example
 * ```ts
 * getIsSlr('SLR_Studio_Title_1080p_12345_LR_180.mp4'); // true
 * getIsSlr('random-video.mp4'); // false
 * ```
 */
export function getIsSlr(filepath: string): boolean {
  return getSlrInfo(filepath) !== null;
}
