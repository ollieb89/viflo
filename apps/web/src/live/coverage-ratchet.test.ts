import { afterEach, describe, expect, it } from 'vitest';
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { execFileSync } from 'node:child_process';

function writeCoverageSummary(dir: string, values: { lines: number; functions: number; branches: number; statements: number }) {
  const coverageDir = join(dir, 'coverage');
  mkdirSync(coverageDir, { recursive: true });

  const summary = {
    total: {
      lines: { pct: values.lines },
      functions: { pct: values.functions },
      branches: { pct: values.branches },
      statements: { pct: values.statements },
    },
  };

  writeFileSync(join(coverageDir, 'coverage-summary.json'), JSON.stringify(summary, null, 2));
}

function writeBaseline(dir: string, values: { lines: number; functions: number; branches: number; statements: number }) {
  const baselineDir = join(dir, '.coverage');
  mkdirSync(baselineDir, { recursive: true });
  writeFileSync(
    join(baselineDir, 'baseline.json'),
    JSON.stringify({ version: '1.0.0', timestamp: '2026-01-01T00:00:00.000Z', coverage: values }, null, 2)
  );
}

describe('coverage-ratchet script', () => {
  const tempDirs: string[] = [];
  const repoRoot = resolve(__dirname, '../../../..');
  const scriptPath = join(repoRoot, 'apps/web/scripts/coverage-ratchet.ts');

  afterEach(() => {
    for (const dir of tempDirs) {
      rmSync(dir, { recursive: true, force: true });
    }
    tempDirs.length = 0;
  });

  function makeTempProject(): string {
    const dir = mkdtempSync(join(tmpdir(), 'viflo-coverage-ratchet-'));
    tempDirs.push(dir);
    return dir;
  }

  it('creates baseline locally when missing', () => {
    const dir = makeTempProject();
    writeCoverageSummary(dir, { lines: 90, functions: 85, branches: 80, statements: 88 });

    execFileSync('npx', ['tsx', scriptPath], { cwd: dir, stdio: 'pipe', encoding: 'utf8' });

    expect(existsSync(join(dir, '.coverage/baseline.json'))).toBe(true);
  });

  it('fails in CI when baseline is missing', () => {
    const dir = makeTempProject();
    writeCoverageSummary(dir, { lines: 90, functions: 85, branches: 80, statements: 88 });

    expect(() =>
      execFileSync('npx', ['tsx', scriptPath], {
        cwd: dir,
        stdio: 'pipe',
        encoding: 'utf8',
        env: { ...process.env, CI: 'true' },
      })
    ).toThrow();
  });

  it('does not auto-update baseline on improved coverage in check mode', () => {
    const dir = makeTempProject();
    writeCoverageSummary(dir, { lines: 95, functions: 90, branches: 85, statements: 92 });
    writeBaseline(dir, { lines: 90, functions: 85, branches: 80, statements: 88 });

    execFileSync('npx', ['tsx', scriptPath], { cwd: dir, stdio: 'pipe', encoding: 'utf8' });

    const baseline = JSON.parse(readFileSync(join(dir, '.coverage/baseline.json'), 'utf8'));
    expect(baseline.coverage.lines).toBe(90);
  });
});
