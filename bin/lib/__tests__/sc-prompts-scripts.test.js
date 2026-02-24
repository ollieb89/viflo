'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

describe('SC prompt scripts', () => {
  const repoRoot = path.resolve(__dirname, '..', '..', '..');
  const validateScript = path.join(repoRoot, 'scripts', 'validate-sc-prompts.sh');
  const benchmarkScript = path.join(repoRoot, 'scripts', 'benchmark-sc-reflect.sh');

  it('validate-sc-prompts succeeds when required files exist and schema keys are present', () => {
    expect(() =>
      execFileSync(validateScript, [], {
        cwd: repoRoot,
        stdio: 'pipe',
        encoding: 'utf8',
      })
    ).not.toThrow();
  });

  it('benchmark-sc-reflect succeeds with default thresholds', () => {
    expect(() =>
      execFileSync(benchmarkScript, [], {
        cwd: repoRoot,
        stdio: 'pipe',
        encoding: 'utf8',
      })
    ).not.toThrow();
  });

  it('validate-sc-prompts fails in a temp repo missing paired prompt files', () => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'viflo-sc-validate-'));

    try {
      fs.mkdirSync(path.join(tmpDir, 'prompts'), { recursive: true });
      fs.mkdirSync(path.join(tmpDir, 'commands', 'sg'), { recursive: true });
      fs.writeFileSync(path.join(tmpDir, 'prompts', 'orphan.md'), '# orphan\n', 'utf8');

      expect(() =>
        execFileSync(validateScript, [], {
          cwd: tmpDir,
          stdio: 'pipe',
          encoding: 'utf8',
        })
      ).toThrow(/missing matching \.toml/);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });
});
