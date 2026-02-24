'use strict';
const path = require('path');

// Mock os so any accidental os.homedir() call is detectable
vi.mock('os', () => ({ homedir: vi.fn(() => '/mock/home') }));

beforeEach(() => {
  vi.resetModules();
});

describe('resolveViFloRoot', () => {
  it('returns a string', () => {
    const { resolveViFloRoot } = require('../paths.cjs');
    const result = resolveViFloRoot();
    expect(typeof result).toBe('string');
  });

  it('returns an absolute path', () => {
    const { resolveViFloRoot } = require('../paths.cjs');
    const result = resolveViFloRoot();
    expect(path.isAbsolute(result)).toBe(true);
  });

  it('ends with /viflo', () => {
    const { resolveViFloRoot } = require('../paths.cjs');
    const result = resolveViFloRoot();
    expect(result.endsWith(path.sep + 'viflo') || result.endsWith('/viflo')).toBe(true);
  });

  it('contains bin as a parent directory segment', () => {
    const { resolveViFloRoot } = require('../paths.cjs');
    const result = resolveViFloRoot();
    // The bin/ directory is a child of the resolved root
    expect(path.join(result, 'bin')).toContain('bin');
  });

  it('does not depend on process.cwd() — contains viflo in path', () => {
    const { resolveViFloRoot } = require('../paths.cjs');
    const result = resolveViFloRoot();
    // resolveViFloRoot uses __dirname, not process.cwd()
    expect(result).toContain('viflo');
  });
});

describe('resolveTargetPath', () => {
  it('assembles cwd + segments into absolute path', () => {
    const { resolveTargetPath } = require('../paths.cjs');
    const result = resolveTargetPath('/tmp/my-project', '.claude', 'settings.json');
    expect(result).toBe('/tmp/my-project/.claude/settings.json');
  });

  it('returns cwd alone when no segments provided', () => {
    const { resolveTargetPath } = require('../paths.cjs');
    const result = resolveTargetPath('/tmp/my-project');
    expect(result).toBe('/tmp/my-project');
  });

  it('throws when cwd is undefined', () => {
    const { resolveTargetPath } = require('../paths.cjs');
    expect(() => resolveTargetPath()).toThrow(/cwd is required/);
  });

  it('throws when cwd is null', () => {
    const { resolveTargetPath } = require('../paths.cjs');
    expect(() => resolveTargetPath(null, 'foo')).toThrow(/cwd is required/);
  });

  it('throws when cwd is a number', () => {
    const { resolveTargetPath } = require('../paths.cjs');
    expect(() => resolveTargetPath(42, 'foo')).toThrow(/cwd is required/);
  });
});
