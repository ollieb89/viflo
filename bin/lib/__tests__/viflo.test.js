'use strict';

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const cliPath = path.resolve(__dirname, '../../viflo.cjs');

let tmpDir;

beforeEach(() => {
  vi.resetModules();
  tmpDir = fs.mkdtempSync('/tmp/viflo-cli-test-');
});

afterEach(() => {
  fs.rmSync(tmpDir, { recursive: true, force: true });
  vi.restoreAllMocks();
});

describe('viflo init --minimal', () => {
  it('fresh project — creates CLAUDE.md with sentinel markers', () => {
    const result = spawnSync(process.execPath, [cliPath, 'init', '--minimal', tmpDir], {
      encoding: 'utf-8',
    });
    expect(result.status).toBe(0);
    const claudeMd = path.join(tmpDir, 'CLAUDE.md');
    expect(fs.existsSync(claudeMd)).toBe(true);
    const content = fs.readFileSync(claudeMd, 'utf-8');
    expect(content).toContain('<!-- BEGIN VIFLO -->');
    expect(content).toContain('<!-- END VIFLO -->');
  });

  it('CLAUDE.md contains @-import lines from viflo skills', () => {
    spawnSync(process.execPath, [cliPath, 'init', '--minimal', tmpDir], { encoding: 'utf-8' });
    const content = fs.readFileSync(path.join(tmpDir, 'CLAUDE.md'), 'utf-8');
    expect(content).toMatch(/^@.*SKILL\.md$/m);
  });

  it('fresh project — creates .claude/settings.json with permissions.allow array', () => {
    spawnSync(process.execPath, [cliPath, 'init', '--minimal', tmpDir], { encoding: 'utf-8' });
    const settingsPath = path.join(tmpDir, '.claude', 'settings.json');
    expect(fs.existsSync(settingsPath)).toBe(true);
    const parsed = JSON.parse(fs.readFileSync(settingsPath, 'utf-8'));
    expect(Array.isArray(parsed.permissions.allow)).toBe(true);
    expect(parsed.permissions.allow.length).toBeGreaterThan(0);
  });

  it('idempotency — second run exits 0 and skips both files', () => {
    spawnSync(process.execPath, [cliPath, 'init', '--minimal', tmpDir], { encoding: 'utf-8' });
    const contentAfterFirst = fs.readFileSync(path.join(tmpDir, 'CLAUDE.md'), 'utf-8');

    const secondResult = spawnSync(process.execPath, [cliPath, 'init', '--minimal', tmpDir], {
      encoding: 'utf-8',
    });
    expect(secondResult.status).toBe(0);

    const contentAfterSecond = fs.readFileSync(path.join(tmpDir, 'CLAUDE.md'), 'utf-8');
    expect(contentAfterSecond).toBe(contentAfterFirst);

    expect(secondResult.stdout).toContain('skipped');
  });

  it('invalid path exits non-zero with "Directory not found" in stderr', () => {
    const result = spawnSync(
      process.execPath,
      [cliPath, 'init', '--minimal', '/nonexistent/viflo-test-path-does-not-exist'],
      { encoding: 'utf-8' }
    );
    expect(result.status).not.toBe(0);
    expect(result.stderr).toContain('Directory not found');
  });

  it('optional positional path argument — uses given path, not process.cwd()', () => {
    const result = spawnSync(process.execPath, [cliPath, 'init', '--minimal', tmpDir], {
      encoding: 'utf-8',
    });
    expect(result.status).toBe(0);
    // File must be in tmpDir, not process.cwd()
    expect(fs.existsSync(path.join(tmpDir, 'CLAUDE.md'))).toBe(true);
    expect(fs.existsSync(path.join(process.cwd(), 'CLAUDE.md'))).toBe(false);
  });

  it('stdout reports created status for new files', () => {
    const result = spawnSync(process.execPath, [cliPath, 'init', '--minimal', tmpDir], {
      encoding: 'utf-8',
    });
    expect(result.status).toBe(0);
    expect(result.stdout).toContain('[viflo] CLAUDE.md: created');
    expect(result.stdout).toContain('[viflo] .claude/settings.json: created');
  });
});

describe('viflo init --full', () => {
  it('fresh project — creates .planning/ with all four stub files', () => {
    const result = spawnSync(process.execPath, [cliPath, 'init', '--full', tmpDir], {
      encoding: 'utf-8',
    });
    expect(result.status).toBe(0);
    expect(fs.existsSync(path.join(tmpDir, '.planning', 'PROJECT.md'))).toBe(true);
    expect(fs.existsSync(path.join(tmpDir, '.planning', 'STATE.md'))).toBe(true);
    expect(fs.existsSync(path.join(tmpDir, '.planning', 'ROADMAP.md'))).toBe(true);
    expect(fs.existsSync(path.join(tmpDir, '.planning', 'config.json'))).toBe(true);
  });

  it('fresh project — config.json is valid JSON with GSD defaults', () => {
    spawnSync(process.execPath, [cliPath, 'init', '--full', tmpDir], { encoding: 'utf-8' });
    const configPath = path.join(tmpDir, '.planning', 'config.json');
    const parsed = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
    expect(parsed.profile).toBe('balanced');
    expect(typeof parsed.workflow).toBe('object');
    expect(parsed.workflow.plan_check).toBe(true);
  });

  it('fresh project — CLAUDE.md contains project sections and sentinel block', () => {
    spawnSync(process.execPath, [cliPath, 'init', '--full', tmpDir], { encoding: 'utf-8' });
    const content = fs.readFileSync(path.join(tmpDir, 'CLAUDE.md'), 'utf-8');
    expect(content).toContain('# Project');
    expect(content).toContain('## Tech Stack');
    expect(content).toContain('## Development Workflow');
    expect(content).toContain('<!-- BEGIN VIFLO -->');
    expect(content).toContain('<!-- END VIFLO -->');
    // Project sections must appear BEFORE the sentinel block
    const sentinelIdx = content.indexOf('<!-- BEGIN VIFLO -->');
    const projectIdx = content.indexOf('# Project');
    expect(projectIdx).toBeLessThan(sentinelIdx);
  });

  it('CLAUDE.md already exists — only sentinel block updated, not replaced', () => {
    const existingContent = '# My Existing Project\n\nSome content I wrote.\n';
    fs.writeFileSync(path.join(tmpDir, 'CLAUDE.md'), existingContent, 'utf-8');

    spawnSync(process.execPath, [cliPath, 'init', '--full', tmpDir], { encoding: 'utf-8' });

    const content = fs.readFileSync(path.join(tmpDir, 'CLAUDE.md'), 'utf-8');
    expect(content).toContain('# My Existing Project');
    expect(content).toContain('Some content I wrote.');
    expect(content).toContain('<!-- BEGIN VIFLO -->');
    expect(content).toContain('<!-- END VIFLO -->');
    // Template sections must NOT appear (CLAUDE.md was not replaced)
    expect(content).not.toContain('## Tech Stack');
  });

  it('idempotency — second --full run exits 0 and skips all existing files', () => {
    spawnSync(process.execPath, [cliPath, 'init', '--full', tmpDir], { encoding: 'utf-8' });
    const projectMdFirst = fs.readFileSync(path.join(tmpDir, '.planning', 'PROJECT.md'), 'utf-8');

    const secondResult = spawnSync(process.execPath, [cliPath, 'init', '--full', tmpDir], {
      encoding: 'utf-8',
    });
    expect(secondResult.status).toBe(0);
    // No file content changed
    const projectMdSecond = fs.readFileSync(path.join(tmpDir, '.planning', 'PROJECT.md'), 'utf-8');
    expect(projectMdSecond).toBe(projectMdFirst);
    // Output indicates skipped
    expect(secondResult.stdout).toContain('skipped');
  });

  it('per-file idempotency — pre-existing .planning/ file is skipped, missing file is created', () => {
    // Pre-create only STATE.md with custom content
    fs.mkdirSync(path.join(tmpDir, '.planning'), { recursive: true });
    const customState = '# My Custom State\n';
    fs.writeFileSync(path.join(tmpDir, '.planning', 'STATE.md'), customState, 'utf-8');

    spawnSync(process.execPath, [cliPath, 'init', '--full', tmpDir], { encoding: 'utf-8' });

    // STATE.md must be unchanged
    const stateContent = fs.readFileSync(path.join(tmpDir, '.planning', 'STATE.md'), 'utf-8');
    expect(stateContent).toBe(customState);
    // Other scaffold files must have been created
    expect(fs.existsSync(path.join(tmpDir, '.planning', 'PROJECT.md'))).toBe(true);
    expect(fs.existsSync(path.join(tmpDir, '.planning', 'config.json'))).toBe(true);
  });

  it('output — summary line shows created count on first run', () => {
    const result = spawnSync(process.execPath, [cliPath, 'init', '--full', tmpDir], {
      encoding: 'utf-8',
    });
    expect(result.status).toBe(0);
    expect(result.stdout).toMatch(/Done\. \d+ files? created, \d+ skipped\./);
  });

  it('output — first-run nudge appears when all files are created', () => {
    const result = spawnSync(process.execPath, [cliPath, 'init', '--full', tmpDir], {
      encoding: 'utf-8',
    });
    expect(result.status).toBe(0);
    expect(result.stdout).toContain('Next:');
  });

  it('output — first-run nudge absent on repeat run', () => {
    spawnSync(process.execPath, [cliPath, 'init', '--full', tmpDir], { encoding: 'utf-8' });
    const secondResult = spawnSync(process.execPath, [cliPath, 'init', '--full', tmpDir], {
      encoding: 'utf-8',
    });
    expect(secondResult.status).toBe(0);
    expect(secondResult.stdout).not.toContain('Next:');
  });

  it('--minimal flag still exits 0 and creates CLAUDE.md + settings.json', () => {
    const result = spawnSync(process.execPath, [cliPath, 'init', '--minimal', tmpDir], {
      encoding: 'utf-8',
    });
    expect(result.status).toBe(0);
    expect(fs.existsSync(path.join(tmpDir, 'CLAUDE.md'))).toBe(true);
    expect(fs.existsSync(path.join(tmpDir, '.claude', 'settings.json'))).toBe(true);
    // .planning/ must NOT be created by --minimal
    expect(fs.existsSync(path.join(tmpDir, '.planning'))).toBe(false);
  });
});
