/**
 * stash-vroom - Utilities for VR video file detection and metadata parsing
 *
 * @packageDocumentation
 */

// JAV detection
export { getJavInfo, getIsJav, matchJavFilename } from './jav.js';
export type { JavInfo } from './jav.js';

// SLR detection
export { getSlrInfo, getIsSlr, getSlrRe } from './slr.js';
export type { SlrInfo, SlrReOptions } from './slr.js';

// Utilities
export { getVidRe, basename } from './util.js';
