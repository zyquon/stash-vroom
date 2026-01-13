#!/usr/bin/env node
/**
 * Bundle stash-vroom for standalone browser use.
 *
 * Creates a single IIFE file that exposes window.StashVroom with all exports.
 * This is used by browser extensions and other non-module environments.
 *
 * Usage: node scripts/bundle-browser.js
 * Output: dist/stash-vroom.browser.js
 */

import { readFileSync, writeFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const distDir = join(__dirname, '..', 'dist');
const outFile = join(distDir, 'stash-vroom.browser.js');

// Read compiled JS files (order matters for dependencies)
const files = ['util.js', 'slr.js', 'jav.js'];

function stripModuleSyntax(code, filename) {
  // Remove import statements
  code = code.replace(/^import\s+\{[^}]+\}\s+from\s+['"][^'"]+['"];\s*$/gm, '');

  // Remove export keywords from function declarations
  code = code.replace(/^export\s+function\s+/gm, 'function ');

  // Remove export keywords from const declarations
  code = code.replace(/^export\s+const\s+/gm, 'const ');

  // Remove standalone export statements
  code = code.replace(/^export\s+\{[^}]+\};\s*$/gm, '');

  // Remove JSDoc module tags
  code = code.replace(/\/\*\*[\s\S]*?@module[\s\S]*?\*\/\s*/g, '');

  // Remove other multi-line JSDoc comments (keep single-line comments)
  code = code.replace(/\/\*\*[\s\S]*?\*\/\s*/g, '');

  return code.trim();
}

// Build the bundle
let bundleBody = '';

for (const file of files) {
  const filepath = join(distDir, file);
  const code = readFileSync(filepath, 'utf-8');
  const stripped = stripModuleSyntax(code, file);
  bundleBody += `  // === ${file} ===\n`;
  bundleBody += stripped.split('\n').map(line => '  ' + line).join('\n');
  bundleBody += '\n\n';
}

// Create the IIFE wrapper with exports
const bundle = `/**
 * stash-vroom - Bundled for browser/extension use
 * Generated from: js/dist/
 *
 * Exposes: window.StashVroom = { getJavInfo, getIsJav, matchJavFilename, getSlrInfo, getIsSlr, getSlrRe, getVidRe, basename }
 */
(function(global) {
  'use strict';

${bundleBody}
  // Export to global
  global.StashVroom = {
    getJavInfo,
    getIsJav,
    matchJavFilename,
    getSlrInfo,
    getIsSlr,
    getSlrRe,
    getVidRe,
    basename,
  };

})(typeof window !== 'undefined' ? window : this);
`;

writeFileSync(outFile, bundle);
console.log(`Wrote browser bundle to ${outFile}`);
