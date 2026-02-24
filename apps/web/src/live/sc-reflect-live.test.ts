import { describe, it, expect } from 'vitest';
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { getRepositoryRoot, validateScReflectArtifacts } from './sc-reflect-live';

describe('SC reflect live repository validation', () => {
  it('finds repository root and confirms required files exist', () => {
    const repoRoot = getRepositoryRoot();
    const result = validateScReflectArtifacts(repoRoot);

    expect(result.missing).toEqual([]);
  });

  it('validates required markers across prompt, template, SG mirror, and index', () => {
    const repoRoot = getRepositoryRoot();
    const result = validateScReflectArtifacts(repoRoot);

    expect(result.markerFailures).toEqual([]);
    expect(result.isValid).toBe(true);
  });

  it('throws when repository markers cannot be found from the start directory', () => {
    const tmp = mkdtempSync(join(tmpdir(), 'viflo-live-root-miss-'));
    try {
      expect(() => getRepositoryRoot(tmp)).toThrow(/Repository root not found/);
    } finally {
      rmSync(tmp, { recursive: true, force: true });
    }
  });

  it('reports missing files and missing marker failures', () => {
    const tmp = mkdtempSync(join(tmpdir(), 'viflo-live-artifacts-'));
    try {
      mkdirSync(join(tmp, 'prompts'), { recursive: true });
      mkdirSync(join(tmp, 'commands', 'sg'), { recursive: true });

      writeFileSync(join(tmp, 'prompts', 'sc-reflect.md'), '# /sc:reflect - Task Reflection and Validation\n');
      writeFileSync(join(tmp, 'prompts', 'sc-reflect.toml'), 'name = \"sc-reflect\"\n');
      writeFileSync(join(tmp, 'commands', 'sg', 'reflect.md'), '# SG Command: /sc:reflect\n');
      // Intentionally omit INDEX.md to hit missing branch.

      const result = validateScReflectArtifacts(tmp);

      expect(result.isValid).toBe(false);
      expect(result.missing).toContain('INDEX.md');
      expect(result.markerFailures.length).toBeGreaterThan(0);
    } finally {
      rmSync(tmp, { recursive: true, force: true });
    }
  });
});
