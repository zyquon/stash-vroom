/**
 * Utilities for VR video file handling.
 *
 * @module util
 */

const DEFAULT_VIDEO_EXTENSIONS = ['mp4', 'm4v', 'mkv', 'avi', 'webm', 'wmv', 'mov'];

/**
 * Return a regular expression pattern to match video file extensions.
 *
 * @param extensions - List of file extensions to match (without dots)
 * @returns A regex pattern string that matches video file extensions
 *
 * @example
 * ```ts
 * const pattern = getVidRe();
 * // Returns: "\\.(mp4|m4v|mkv|avi|webm|wmv|mov)$"
 * ```
 */
export function getVidRe(extensions: string[] = DEFAULT_VIDEO_EXTENSIONS): string {
  // Remove empty strings and duplicates
  const cleaned = [...new Set(extensions.filter((x) => x))];

  // Escape special regex characters
  const escaped = cleaned.map((ext) => ext.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));

  return '\\.(' + escaped.join('|') + ')$';
}

/**
 * Extract the basename from a file path.
 *
 * Works with both Unix and Windows path separators.
 *
 * @param filepath - A file path
 * @returns The basename (filename) portion of the path
 */
export function basename(filepath: string): string {
  // Handle both Unix and Windows separators
  const lastSlash = Math.max(filepath.lastIndexOf('/'), filepath.lastIndexOf('\\'));
  return lastSlash === -1 ? filepath : filepath.slice(lastSlash + 1);
}
