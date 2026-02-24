'use strict';

const fs = require('fs');
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

// Find optional positional target path: the first arg after index 1 that
// does not start with '--'
const positional = args.slice(1).find((a) => !a.startsWith('--'));
const targetDir = positional !== undefined ? positional : process.cwd();

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

if (subcommand !== 'init') {
  process.stderr.write('Usage: viflo init --minimal [path]\n       viflo init --full [path]\n');
  process.exit(1);
}

if (!hasMinimalFlag && !hasFullFlag) {
  process.stderr.write('Usage: viflo init --minimal [path]\n       viflo init --full [path]\n');
  process.exit(1);
}

if (!fs.existsSync(targetDir)) {
  process.stderr.write('Directory not found: ' + targetDir + '\n');
  process.exit(1);
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
// --minimal mode (unchanged behaviour)
// ---------------------------------------------------------------------------

if (hasMinimalFlag && !hasFullFlag) {
  const claudeResult = writeCLAUDEmd(targetDir, sentinelContent);
  const settingsResult = writeSettingsJson(targetDir, defaultSettings);
  const claudeStatus = claudeResult.written ? claudeResult.reason : 'skipped';
  const settingsStatus = settingsResult.written ? settingsResult.reason : 'skipped';
  console.log('[viflo] CLAUDE.md: ' + claudeStatus);
  console.log('[viflo] .claude/settings.json: ' + settingsStatus);
  process.exit(0);
}

// ---------------------------------------------------------------------------
// --full mode
// ---------------------------------------------------------------------------

if (hasFullFlag) {
  // Step 1: CLAUDE.md — richer template or sentinel-only merge
  const claudeResult = writeCLAUDEmdTemplate(targetDir, sentinelContent);
  // Step 2: settings.json — same as --minimal
  const settingsResult = writeSettingsJson(targetDir, defaultSettings);
  // Step 3: .planning/ scaffold — four stub files
  const scaffoldResults = writePlanningScaffold(targetDir);

  // Build full results list for output
  const allResults = [
    { label: 'CLAUDE.md', written: claudeResult.written, reason: claudeResult.reason },
    { label: '.claude/settings.json', written: settingsResult.written, reason: settingsResult.reason },
    ...scaffoldResults.map(r => ({
      label: r.path,
      written: r.written,
      reason: r.reason,
    })),
  ];

  let created = 0;
  let skipped = 0;
  for (const r of allResults) {
    if (r.written) {
      console.log('  created  ' + r.label);
      created++;
    } else {
      console.log('  skipped  ' + r.label + ' (' + (r.reason || 'already exists') + ')');
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
