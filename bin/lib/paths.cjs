'use strict';

const path = require('path');

/**
 * Resolve the viflo installation root.
 * paths.cjs lives at bin/lib/paths.cjs — two levels up is the repo root.
 * Never uses process.cwd() or os.homedir().
 *
 * @returns {string} Absolute path to the viflo repo root.
 */
function resolveViFloRoot() {
  return path.resolve(__dirname, '..', '..');
}

/**
 * Resolve an absolute path within a target project directory.
 *
 * @param {string} cwd - Explicit working directory of the target project (required).
 * @param {...string} segments - Path segments relative to cwd.
 * @returns {string} Absolute path string.
 */
function resolveTargetPath(cwd, ...segments) {
  if (!cwd || typeof cwd !== 'string') {
    throw new Error('resolveTargetPath: cwd is required and must be a string');
  }
  return path.resolve(cwd, ...segments);
}

module.exports = { resolveViFloRoot, resolveTargetPath };
