import { afterEach, describe, expect, it } from 'vitest';
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { createRequire } from 'node:module';

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
  const scriptPath = join(repoRoot, 'apps/web/scripts/coverage-ratchet.cjs');
  const require = createRequire(import.meta.url);
  const coverageRatchet = require(scriptPath) as { main: () => void };

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

  function runRatchet(cwd: string, args: string[] = [], envOverrides: Record<string, string | undefined> = {}): number {
    const previousArgv = process.argv.slice();
    const previousEnv = { ...process.env };
    const exitToken = Symbol('process.exit');
    let exitCode = 0;

    const originalExit = process.exit;
    process.exit = ((code?: number) => {
      exitCode = code ?? 0;
      throw exitToken;
    }) as typeof process.exit;

    try {
      process.argv = ['node', scriptPath, ...args];
      process.env.COVERAGE_RATCHET_CWD = cwd;

      for (const [key, value] of Object.entries(envOverrides)) {
        if (value === undefined) {
          delete process.env[key];
        } else {
          process.env[key] = value;
        }
      }

      try {
        coverageRatchet.main();
      } catch (error) {
        if (error !== exitToken) {
          throw error;
        }
      }
    } finally {
      process.exit = originalExit;
      process.argv = previousArgv;

      // Reset env to avoid cross-test leakage.
      for (const key of Object.keys(process.env)) {
        if (!(key in previousEnv)) {
          delete process.env[key];
        }
      }
      for (const [key, value] of Object.entries(previousEnv)) {
        process.env[key] = value;
      }
    }

    return exitCode;
  }

  it('creates baseline locally when missing', () => {
    const dir = makeTempProject();
    writeCoverageSummary(dir, { lines: 90, functions: 85, branches: 80, statements: 88 });

    const exitCode = runRatchet(dir);

    expect(exitCode).toBe(0);
    expect(existsSync(join(dir, '.coverage/baseline.json'))).toBe(true);
  });

  it('fails in CI when baseline is missing', () => {
    const dir = makeTempProject();
    writeCoverageSummary(dir, { lines: 90, functions: 85, branches: 80, statements: 88 });

    const exitCode = runRatchet(dir, [], { CI: 'true' });
    expect(exitCode).toBe(1);
  });

  it('does not auto-update baseline on improved coverage in check mode', () => {
    const dir = makeTempProject();
    writeCoverageSummary(dir, { lines: 95, functions: 90, branches: 85, statements: 92 });
    writeBaseline(dir, { lines: 90, functions: 85, branches: 80, statements: 88 });

    const exitCode = runRatchet(dir);

    expect(exitCode).toBe(0);
    const baseline = JSON.parse(readFileSync(join(dir, '.coverage/baseline.json'), 'utf8'));
    expect(baseline.coverage.lines).toBe(90);
  });
});
