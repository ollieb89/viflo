'use strict';

const fs = require('fs');
const { resolveViFloRoot, resolveTargetPath } = require('./lib/paths.cjs');
const { writeCLAUDEmd, writeSettingsJson } = require('./lib/writers.cjs');
const { scanSkills } = require('./lib/skills.cjs');

// ---------------------------------------------------------------------------
// Argument parsing
// ---------------------------------------------------------------------------

const args = process.argv.slice(2);
const subcommand = args[0];
const hasMinimalFlag = args.includes('--minimal');

// Find optional positional target path: the first arg after index 1 that
// does not start with '--'
const positional = args.slice(1).find((a) => !a.startsWith('--'));
const targetDir = positional !== undefined ? positional : process.cwd();

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

if (subcommand !== 'init') {
  process.stderr.write('Usage: viflo init --minimal [path]\n');
  process.exit(1);
}

if (!hasMinimalFlag) {
  process.stderr.write('Usage: viflo init --minimal [path]\n');
  process.exit(1);
}

if (!fs.existsSync(targetDir)) {
  process.stderr.write('Directory not found: ' + targetDir + '\n');
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Core logic
// ---------------------------------------------------------------------------

const viFloRoot = resolveViFloRoot();
const importLines = scanSkills(viFloRoot);
const sentinelContent = importLines.join('\n');

const defaultSettings = {
  permissions: {
    allow: ['Bash', 'Read', 'Write', 'Edit', 'Glob', 'Grep', 'WebFetch', 'mcp__*'],
  },
};

const claudeResult = writeCLAUDEmd(targetDir, sentinelContent);
const settingsResult = writeSettingsJson(targetDir, defaultSettings);

// ---------------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------------

const claudeStatus = claudeResult.written ? claudeResult.reason : 'skipped';
const settingsStatus = settingsResult.written ? settingsResult.reason : 'skipped';

console.log('[viflo] CLAUDE.md: ' + claudeStatus);
console.log('[viflo] .claude/settings.json: ' + settingsStatus);

process.exit(0);
