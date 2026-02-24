'use strict';

const fs = require('fs');
const path = require('path');
const { resolveTargetPath } = require('./paths.cjs');

const SENTINEL_START = '<!-- BEGIN VIFLO -->';
const SENTINEL_END   = '<!-- END VIFLO -->';

/**
 * Write newContent to filePath only if it differs from existing content.
 * Creates parent directories if needed.
 *
 * @param {string} filePath - Absolute path to write.
 * @param {string} newContent - Content to write.
 * @returns {{ written: boolean, reason: string, filePath: string }}
 */
function writeIfChanged(filePath, newContent) {
  let existing = null;
  try {
    existing = fs.readFileSync(filePath, 'utf-8');
  } catch (err) {
    if (err.code !== 'ENOENT') throw err;
  }

  if (existing === newContent) {
    return { written: false, reason: 'skipped', filePath };
  }

  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, newContent, 'utf-8');
  return { written: true, reason: existing === null ? 'created' : 'updated', filePath };
}

/**
 * Merge sentinelContent into existingContent using VIFLO sentinel markers.
 * Appends a new sentinel block if none exists; replaces the block if one exists.
 * Throws if multiple sentinel blocks are detected.
 *
 * @param {string} existingContent
 * @param {string} sentinelContent
 * @returns {string}
 */
function mergeCLAUDEmd(existingContent, sentinelContent) {
  const startCount = existingContent.split(SENTINEL_START).length - 1;
  const endCount   = existingContent.split(SENTINEL_END).length - 1;

  if (startCount > 1 || endCount > 1) {
    throw new Error(
      '[viflo] CLAUDE.md contains multiple sentinel blocks. Remove duplicates manually before running viflo init.'
    );
  }

  const block = SENTINEL_START + '\n' + sentinelContent + '\n' + SENTINEL_END;

  if (startCount === 0) {
    return existingContent.trimEnd() + '\n\n' + block + '\n';
  }

  // startCount === 1: replace existing block
  const startIdx = existingContent.indexOf(SENTINEL_START);
  const endIdx   = existingContent.indexOf(SENTINEL_END);
  return (
    existingContent.slice(0, startIdx) +
    block +
    existingContent.slice(endIdx + SENTINEL_END.length)
  );
}

/**
 * Recursively merge incoming into a shallow copy of existing.
 * Arrays: deduplicate with existing-first order.
 * Objects: recurse.
 * Scalars / type mismatch: incoming wins.
 * Unknown keys in existing are preserved.
 *
 * @param {Object} existing
 * @param {Object} incoming
 * @returns {Object}
 */
function deepMerge(existing, incoming) {
  const result = Object.assign({}, existing);

  for (const key of Object.keys(incoming)) {
    const existingVal = existing[key];
    const incomingVal = incoming[key];

    if (Array.isArray(existingVal) && Array.isArray(incomingVal)) {
      result[key] = [...new Set([...existingVal, ...incomingVal])];
    } else if (
      existingVal !== null &&
      incomingVal !== null &&
      typeof existingVal === 'object' &&
      typeof incomingVal === 'object' &&
      !Array.isArray(existingVal) &&
      !Array.isArray(incomingVal)
    ) {
      result[key] = deepMerge(existingVal, incomingVal);
    } else {
      result[key] = incomingVal;
    }
  }

  return result;
}

/**
 * Write the viflo sentinel block into the target project's CLAUDE.md.
 * Creates the file if it does not exist. Replaces the block if it does.
 * Idempotent: second call with same content returns { written: false, reason: 'skipped', filePath }.
 *
 * @param {string} targetCwd - Absolute path to the target project root.
 * @param {string} sentinelContent - Content to place between sentinel markers.
 * @returns {{ written: boolean, reason: string, filePath: string }}
 */
function writeCLAUDEmd(targetCwd, sentinelContent) {
  const filePath = resolveTargetPath(targetCwd, 'CLAUDE.md');

  let existingContent = null;
  try {
    existingContent = fs.readFileSync(filePath, 'utf-8');
  } catch (err) {
    if (err.code !== 'ENOENT') throw err;
  }

  let newContent;
  if (existingContent === null) {
    newContent = SENTINEL_START + '\n' + sentinelContent + '\n' + SENTINEL_END + '\n';
  } else {
    newContent = mergeCLAUDEmd(existingContent, sentinelContent);
  }

  return writeIfChanged(filePath, newContent);
}

/**
 * Write viflo settings into the target project's .claude/settings.json.
 * Deep-merges with existing content. Deduplicates arrays (existing items first).
 * Idempotent: second call with same settings returns { written: false, reason: 'skipped', filePath }.
 *
 * @param {string} targetCwd - Absolute path to the target project root.
 * @param {Object} incomingSettings - Settings object to merge in.
 * @returns {{ written: boolean, reason: string, filePath: string }}
 */
function writeSettingsJson(targetCwd, incomingSettings) {
  const filePath = resolveTargetPath(targetCwd, '.claude', 'settings.json');

  let existing = {};
  try {
    existing = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  } catch (err) {
    if (err.code !== 'ENOENT') throw err;
  }

  const merged = deepMerge(existing, incomingSettings);
  const newContent = JSON.stringify(merged, null, 2) + '\n';

  return writeIfChanged(filePath, newContent);
}

/**
 * Write four stub files into {targetCwd}/.planning/.
 * Each file is written only if it does not already exist.
 *
 * @param {string} targetCwd - Absolute path to the target project root.
 * @returns {Array<{ path: string, filePath: string, written: boolean, reason: string }>}
 */
function writePlanningScaffold(targetCwd) {
  const planningDir = path.join(targetCwd, '.planning');
  fs.mkdirSync(planningDir, { recursive: true });

  const stubs = [
    {
      relPath: '.planning/PROJECT.md',
      content: '# Project\n\n## Goals\n\n## Stack\n\n## Architecture\n\n## Conventions\n',
    },
    {
      relPath: '.planning/ROADMAP.md',
      content: [
        '# Roadmap',
        '',
        '## Milestones',
        '',
        '### \uD83D\uDCCB v1.0 MVP',
        '',
        '## Phases',
        '',
        '<!-- Example phase entry \u2014 fill in your own below:',
        '### Phase 1: Feature Name',
        '**Goal**: What this phase achieves',
        '**Depends on**: Phase 0',
        '**Requirements**: REQ-01, REQ-02',
        '**Plans**: TBD',
        '-->',
        '',
        '## Progress',
        '',
        '| Phase | Plans Complete | Status | Completed |',
        '|-------|----------------|--------|-----------|',
        '',
      ].join('\n'),
    },
    {
      relPath: '.planning/config.json',
      content: JSON.stringify(
        {
          mode: 'interactive',
          depth: 'standard',
          profile: 'balanced',
          workflow: {
            research: false,
            plan_check: true,
            verifier: true,
            auto_advance: false,
          },
          parallelization: {
            enabled: true,
          },
          git: {
            commit_docs: true,
            branching_strategy: 'none',
          },
        },
        null,
        2
      ) + '\n',
    },
    {
      relPath: '.planning/STATE.md',
      content: [
        '# Project State',
        '',
        '## Project Reference',
        '',
        'See: .planning/PROJECT.md',
        '',
        '## Current Position',
        '',
        'Phase: \u2014',
        'Plan: \u2014',
        'Status: Not started',
        '',
        '## Accumulated Context',
        '',
        '### Key Decisions (summary)',
        '',
        '### Pending Todos',
        '',
        '### Blockers/Concerns',
        '',
        'None.',
        '',
        '## Session Continuity',
        '',
        'Last session: \u2014',
        'Stopped at: \u2014',
        'Resume with: /gsd:new-project to plan your first phase',
        '',
      ].join('\n'),
    },
  ];

  const results = [];
  for (const stub of stubs) {
    const filePath = resolveTargetPath(targetCwd, stub.relPath);
    if (fs.existsSync(filePath)) {
      results.push({ path: stub.relPath, filePath, written: false, reason: 'skipped' });
    } else {
      const result = writeIfChanged(filePath, stub.content);
      results.push({ path: stub.relPath, filePath: result.filePath, written: result.written, reason: result.reason });
    }
  }
  return results;
}

/**
 * Write a richer CLAUDE.md starter template when the file does not exist.
 * If CLAUDE.md already exists, falls back to writeCLAUDEmd() (sentinel-only merge).
 *
 * @param {string} targetCwd - Absolute path to the target project root.
 * @param {string} sentinelContent - Content to place between sentinel markers.
 * @returns {{ written: boolean, reason: string, filePath: string }}
 */
function writeCLAUDEmdTemplate(targetCwd, sentinelContent) {
  const filePath = resolveTargetPath(targetCwd, 'CLAUDE.md');

  if (!fs.existsSync(filePath)) {
    const block = SENTINEL_START + '\n' + sentinelContent + '\n' + SENTINEL_END;
    const fullTemplate = [
      '# Project',
      '',
      'A brief description of this project.',
      '',
      '## Tech Stack',
      '',
      '- Language:',
      '- Framework:',
      '- Database:',
      '',
      '## Development Workflow',
      '',
      'This project uses [GSD methodology](https://github.com/olivermonberg/viflo) with `/gsd:` commands.',
      '',
      'Key commands:',
      '- `/gsd:new-project` \u2014 plan and start a new project milestone',
      '- `/gsd:plan-phase N` \u2014 plan a specific phase',
      '- `/gsd:execute-phase N` \u2014 execute a planned phase',
      '',
      block,
      '',
    ].join('\n');
    return writeIfChanged(filePath, fullTemplate);
  }

  return writeCLAUDEmd(targetCwd, sentinelContent);
}

module.exports = { writeCLAUDEmd, writeSettingsJson, writePlanningScaffold, writeCLAUDEmdTemplate };
