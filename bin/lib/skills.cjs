'use strict';

const fs = require('fs');
const path = require('path');

/**
 * Scan the viflo skills directory and return @-import lines for each skill found.
 *
 * @param {string} rootDir - The viflo installation root directory (caller's responsibility).
 * @returns {string[]} Sorted array of @-import lines, one per skill directory found.
 */
function scanSkills(rootDir) {
  const skillsDir = path.join(rootDir, '.agent', 'skills');

  let entries;
  try {
    entries = fs.readdirSync(skillsDir, { withFileTypes: true });
  } catch (err) {
    if (err.code === 'ENOENT') {
      return [];
    }
    throw err;
  }

  const lines = entries
    .filter((entry) => entry.isDirectory())
    .map((entry) => `@${path.join(rootDir, '.agent', 'skills', entry.name, 'SKILL.md')}`);

  lines.sort();
  return lines;
}

module.exports = { scanSkills };
