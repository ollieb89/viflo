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
