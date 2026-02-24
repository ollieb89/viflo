'use strict';

const fs = require('fs');
const path = require('path');
const { resolveViFloRoot, resolveTargetPath } = require('./lib/paths.cjs');
const { writeCLAUDEmd, writeSettingsJson, writePlanningScaffold, writeCLAUDEmdTemplate } = require('./lib/writers.cjs');
const { scanSkills } = require('./lib/skills.cjs');

// ---------------------------------------------------------------------------
// Argument parsing
// ---------------------------------------------------------------------------

const args = process.argv.slice(2);
const subcommand = args[0];
const hasMinimalFlag = args.includes('--minimal');
const hasFullFlag = args.includes('--full');
const hasDryRunFlag = args.includes('--dry-run');

// Find optional positional target path: the first arg after index 1 that
// does not start with '--'
const positional = args.slice(1).find((a) => !a.startsWith('--'));
const targetDir = positional !== undefined ? positional : process.cwd();

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

if (subcommand !== 'init') {
  process.stderr.write('Usage: viflo init --minimal [--dry-run] [path]\n       viflo init --full [--dry-run] [path]\n');
  process.exit(1);
}

if (!hasMinimalFlag && !hasFullFlag) {
  process.stderr.write('Usage: viflo init --minimal [--dry-run] [path]\n       viflo init --full [--dry-run] [path]\n');
  process.exit(1);
}

if (!fs.existsSync(targetDir)) {
  process.stderr.write('Directory not found: ' + targetDir + '\n');
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Output helper
// ---------------------------------------------------------------------------

/**
 * Print a labelled file action result to stdout.
 * Label is padded to 8 chars for column alignment.
 *
 * @param {string} label - e.g. 'created', 'updated', 'skipped', 'merged'
 * @param {string} absolutePath - Resolved absolute path to the file.
 */
function printResult(label, absolutePath) {
  console.log('  ' + label.padEnd(8) + ' ' + absolutePath);
}

// ---------------------------------------------------------------------------
// Dry-run mode
// ---------------------------------------------------------------------------

/**
 * Preview what would happen without touching the filesystem.
 * Prints [dry-run] labelled lines with resolved absolute paths and exits 0.
 *
 * @param {string} targetCwd - Absolute path to the target project root.
 * @param {boolean} isFullMode - Whether --full mode is active.
 */
function runDryRun(targetCwd, isFullMode) {
  const claudePath = resolveTargetPath(targetCwd, 'CLAUDE.md');
  const settingsPath = resolveTargetPath(targetCwd, '.claude', 'settings.json');

  const claudeLabel = fs.existsSync(claudePath) ? '[dry-run] would merge' : '[dry-run] would create';
  const settingsLabel = fs.existsSync(settingsPath) ? '[dry-run] would update' : '[dry-run] would create';

  console.log('  ' + claudeLabel.padEnd(20) + ' ' + claudePath);
  console.log('  ' + settingsLabel.padEnd(20) + ' ' + settingsPath);

  if (isFullMode) {
    const scaffoldFiles = [
      '.planning/PROJECT.md',
      '.planning/STATE.md',
      '.planning/ROADMAP.md',
      '.planning/config.json',
    ];
    for (const relPath of scaffoldFiles) {
      const absPath = resolveTargetPath(targetCwd, relPath);
      const label = fs.existsSync(absPath) ? '[dry-run] would skip' : '[dry-run] would create';
      console.log('  ' + label.padEnd(20) + ' ' + absPath);
    }
  }
}

// ---------------------------------------------------------------------------
// Core logic — shared setup
// ---------------------------------------------------------------------------

const viFloRoot = resolveViFloRoot();
const importLines = scanSkills(viFloRoot);
const sentinelContent = importLines.join('\n');

const defaultSettings = {
  permissions: {
    allow: ['Bash', 'Read', 'Write', 'Edit', 'Glob', 'Grep', 'WebFetch', 'mcp__*'],
  },
};

// ---------------------------------------------------------------------------
// --minimal mode
// ---------------------------------------------------------------------------

if (hasMinimalFlag && !hasFullFlag) {
  if (hasDryRunFlag) {
    runDryRun(targetDir, false);
    process.exit(0);
  }

  const claudeExisted = fs.existsSync(resolveTargetPath(targetDir, 'CLAUDE.md'));
  const settingsExisted = fs.existsSync(resolveTargetPath(targetDir, '.claude', 'settings.json'));

  const claudeResult = writeCLAUDEmd(targetDir, sentinelContent);
  const settingsResult = writeSettingsJson(targetDir, defaultSettings);

  const claudeLabel = claudeResult.written ? (claudeExisted ? 'merged' : 'created') : 'skipped';
  const settingsLabel = settingsResult.written ? (settingsExisted ? 'updated' : 'created') : 'skipped';

  printResult(claudeLabel, claudeResult.filePath);
  printResult(settingsLabel, settingsResult.filePath);

  process.exit(0);
}

// ---------------------------------------------------------------------------
// --full mode
// ---------------------------------------------------------------------------

if (hasFullFlag) {
  if (hasDryRunFlag) {
    runDryRun(targetDir, true);
    process.exit(0);
  }

  const claudeExisted = fs.existsSync(resolveTargetPath(targetDir, 'CLAUDE.md'));
  const settingsExisted = fs.existsSync(resolveTargetPath(targetDir, '.claude', 'settings.json'));

  // Step 1: CLAUDE.md — richer template or sentinel-only merge
  const claudeResult = writeCLAUDEmdTemplate(targetDir, sentinelContent);
  // Step 2: settings.json — same as --minimal
  const settingsResult = writeSettingsJson(targetDir, defaultSettings);
  // Step 3: .planning/ scaffold — four stub files
  const scaffoldResults = writePlanningScaffold(targetDir);

  const claudeLabel = claudeResult.written ? (claudeExisted ? 'merged' : 'created') : 'skipped';
  const settingsLabel = settingsResult.written ? (settingsExisted ? 'updated' : 'created') : 'skipped';

  printResult(claudeLabel, claudeResult.filePath);
  printResult(settingsLabel, settingsResult.filePath);
  for (const r of scaffoldResults) {
    printResult(r.reason, r.filePath);
  }

  let created = 0;
  let skipped = 0;
  const allLabels = [claudeLabel, settingsLabel, ...scaffoldResults.map(r => r.reason)];
  for (const label of allLabels) {
    if (label === 'created' || label === 'updated' || label === 'merged') {
      created++;
    } else {
      skipped++;
    }
  }

  console.log('');
  console.log('Done. ' + created + ' file' + (created !== 1 ? 's' : '') + ' created, ' + skipped + ' skipped.');

  // First-run nudge: only when everything was created (no skips)
  if (skipped === 0) {
    console.log('');
    console.log('Next: edit .planning/PROJECT.md and run /gsd:new-project to plan your first milestone.');
  }

  process.exit(0);
}
