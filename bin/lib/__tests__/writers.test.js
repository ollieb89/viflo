'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');

vi.mock('os', () => ({ homedir: vi.fn(() => '/mock/home') }));

let tmpDir;
beforeEach(() => {
  vi.resetModules();
  tmpDir = fs.mkdtempSync(path.join('/tmp', 'viflo-writers-test-'));
});
afterEach(() => {
  fs.rmSync(tmpDir, { recursive: true, force: true });
  vi.restoreAllMocks();
});

describe('writeCLAUDEmd', () => {
  it('creates CLAUDE.md with sentinel block when file does not exist', () => {
    const { writeCLAUDEmd } = require('../writers.cjs');
    const result = writeCLAUDEmd(tmpDir, 'viflo instructions here');
    const expectedFilePath = path.join(tmpDir, 'CLAUDE.md');
    expect(result).toEqual({ written: true, reason: 'created', filePath: expectedFilePath });
    const content = fs.readFileSync(path.join(tmpDir, 'CLAUDE.md'), 'utf-8');
    expect(content).toContain('<!-- BEGIN VIFLO -->');
    expect(content).toContain('<!-- END VIFLO -->');
    expect(content).toContain('viflo instructions here');
  });

  it('returns { written: false, reason: "skipped" } on second call with same content', () => {
    const { writeCLAUDEmd } = require('../writers.cjs');
    writeCLAUDEmd(tmpDir, 'same content');
    const result = writeCLAUDEmd(tmpDir, 'same content');
    const expectedFilePath = path.join(tmpDir, 'CLAUDE.md');
    expect(result).toEqual({ written: false, reason: 'skipped', filePath: expectedFilePath });
  });

  it('appends sentinel block at end of existing CLAUDE.md with no markers', () => {
    const { writeCLAUDEmd } = require('../writers.cjs');
    const filePath = path.join(tmpDir, 'CLAUDE.md');
    fs.writeFileSync(filePath, '# Existing Content\n\nSome text here.\n', 'utf-8');
    const result = writeCLAUDEmd(tmpDir, 'viflo block');
    expect(result.written).toBe(true);
    const content = fs.readFileSync(filePath, 'utf-8');
    expect(content).toContain('# Existing Content');
    expect(content).toContain('Some text here.');
    expect(content).toContain('<!-- BEGIN VIFLO -->');
    expect(content).toContain('viflo block');
    // Existing content appears before the sentinel block
    expect(content.indexOf('# Existing Content')).toBeLessThan(content.indexOf('<!-- BEGIN VIFLO -->'));
  });

  it('replaces existing sentinel block while preserving content outside it', () => {
    const { writeCLAUDEmd } = require('../writers.cjs');
    const filePath = path.join(tmpDir, 'CLAUDE.md');
    const existing = '# Title\n\n<!-- BEGIN VIFLO -->\nold content\n<!-- END VIFLO -->\n\nAfter block.\n';
    fs.writeFileSync(filePath, existing, 'utf-8');
    const result = writeCLAUDEmd(tmpDir, 'new content');
    expect(result.written).toBe(true);
    const content = fs.readFileSync(filePath, 'utf-8');
    expect(content).toContain('# Title');
    expect(content).toContain('After block.');
    expect(content).toContain('new content');
    expect(content).not.toContain('old content');
  });

  it('throws containing "multiple sentinel" when CLAUDE.md has two sentinel blocks', () => {
    const { writeCLAUDEmd } = require('../writers.cjs');
    const filePath = path.join(tmpDir, 'CLAUDE.md');
    const doubled =
      '<!-- BEGIN VIFLO -->\nfirst\n<!-- END VIFLO -->\n\n<!-- BEGIN VIFLO -->\nsecond\n<!-- END VIFLO -->\n';
    fs.writeFileSync(filePath, doubled, 'utf-8');
    expect(() => writeCLAUDEmd(tmpDir, 'anything')).toThrow(/multiple sentinel/);
  });

  it('uses <!-- BEGIN VIFLO --> and <!-- END VIFLO --> as sentinel constants', () => {
    const { writeCLAUDEmd } = require('../writers.cjs');
    writeCLAUDEmd(tmpDir, 'test content');
    const content = fs.readFileSync(path.join(tmpDir, 'CLAUDE.md'), 'utf-8');
    expect(content).toContain('<!-- BEGIN VIFLO -->');
    expect(content).toContain('<!-- END VIFLO -->');
  });
});

describe('writeSettingsJson', () => {
  it('creates .claude/settings.json when it does not exist', () => {
    const { writeSettingsJson } = require('../writers.cjs');
    const result = writeSettingsJson(tmpDir, { allow: ['Bash(git*)'] });
    const expectedFilePath = path.join(tmpDir, '.claude', 'settings.json');
    expect(result).toEqual({ written: true, reason: 'created', filePath: expectedFilePath });
    const filePath = path.join(tmpDir, '.claude', 'settings.json');
    expect(fs.existsSync(filePath)).toBe(true);
    const parsed = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    expect(parsed.allow).toEqual(['Bash(git*)']);
  });

  it('returns { written: false, reason: "skipped" } on second call with same settings', () => {
    const { writeSettingsJson } = require('../writers.cjs');
    writeSettingsJson(tmpDir, { version: 1 });
    const result = writeSettingsJson(tmpDir, { version: 1 });
    const expectedFilePath = path.join(tmpDir, '.claude', 'settings.json');
    expect(result).toEqual({ written: false, reason: 'skipped', filePath: expectedFilePath });
  });

  it('deep-merges: existing key is preserved when incoming has only a different key', () => {
    const { writeSettingsJson } = require('../writers.cjs');
    const filePath = path.join(tmpDir, '.claude', 'settings.json');
    fs.mkdirSync(path.join(tmpDir, '.claude'), { recursive: true });
    fs.writeFileSync(filePath, JSON.stringify({ foo: 1 }, null, 2) + '\n', 'utf-8');
    writeSettingsJson(tmpDir, { bar: 2 });
    const parsed = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    expect(parsed.foo).toBe(1);
    expect(parsed.bar).toBe(2);
  });

  it('deduplicates arrays with existing items first', () => {
    const { writeSettingsJson } = require('../writers.cjs');
    const filePath = path.join(tmpDir, '.claude', 'settings.json');
    fs.mkdirSync(path.join(tmpDir, '.claude'), { recursive: true });
    fs.writeFileSync(filePath, JSON.stringify({ allow: ['Bash(git*)'] }, null, 2) + '\n', 'utf-8');
    writeSettingsJson(tmpDir, { allow: ['Bash(git*)', 'Bash(npm*)'] });
    const parsed = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    // Exactly one of each, existing item comes first
    expect(parsed.allow).toEqual(['Bash(git*)', 'Bash(npm*)']);
  });

  it('scalar conflict: incoming scalar wins', () => {
    const { writeSettingsJson } = require('../writers.cjs');
    const filePath = path.join(tmpDir, '.claude', 'settings.json');
    fs.mkdirSync(path.join(tmpDir, '.claude'), { recursive: true });
    fs.writeFileSync(filePath, JSON.stringify({ version: 1 }, null, 2) + '\n', 'utf-8');
    writeSettingsJson(tmpDir, { version: 2 });
    const parsed = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    expect(parsed.version).toBe(2);
  });

  it('deep nested merge: merges nested objects without clobbering sibling keys', () => {
    const { writeSettingsJson } = require('../writers.cjs');
    const filePath = path.join(tmpDir, '.claude', 'settings.json');
    fs.mkdirSync(path.join(tmpDir, '.claude'), { recursive: true });
    fs.writeFileSync(
      filePath,
      JSON.stringify({ permissions: { allow: ['A'] } }, null, 2) + '\n',
      'utf-8'
    );
    writeSettingsJson(tmpDir, { permissions: { deny: ['B'] } });
    const parsed = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    expect(parsed.permissions.allow).toEqual(['A']);
    expect(parsed.permissions.deny).toEqual(['B']);
  });

  it('output JSON has trailing newline', () => {
    const { writeSettingsJson } = require('../writers.cjs');
    writeSettingsJson(tmpDir, { foo: 'bar' });
    const raw = fs.readFileSync(path.join(tmpDir, '.claude', 'settings.json'), 'utf-8');
    expect(raw.endsWith('\n')).toBe(true);
  });
});
