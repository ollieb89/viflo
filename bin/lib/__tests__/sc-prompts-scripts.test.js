'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

describe('SC prompt scripts', () => {
  const repoRoot = path.resolve(__dirname, '..', '..', '..');
  const validateScript = path.join(repoRoot, 'scripts', 'validate-sc-prompts.sh');
  const benchmarkScript = path.join(repoRoot, 'scripts', 'benchmark-sc-reflect.sh');
  const packageJsonPath = path.join(repoRoot, 'package.json');
  const huskyPreCommitPath = path.join(repoRoot, '.husky', 'pre-commit');
  const gitleaksConfigPath = path.join(repoRoot, '.gitleaks.toml');

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

  it('root package scripts include husky prepare and gitleaks precommit checks', () => {
    const pkg = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));

    expect(pkg.scripts).toHaveProperty('prepare');
    expect(pkg.scripts.prepare).toMatch(/husky/);

    expect(pkg.scripts).toHaveProperty('precommit:secrets');
    const precommitSecretsScript = pkg.scripts['precommit:secrets'];
    expect(precommitSecretsScript).toBeTruthy();

    if (precommitSecretsScript.includes('gitleaks')) {
      expect(precommitSecretsScript).toContain('gitleaks');
      return;
    }

    const wrapperScript = precommitSecretsScript.replace(/^\.\//, '').split(/\s+/)[0];
    const wrapperPath = path.join(repoRoot, wrapperScript);
    expect(fs.existsSync(wrapperPath)).toBe(true);
    expect(fs.readFileSync(wrapperPath, 'utf8')).toContain('gitleaks');
  });

  it('pre-commit hook calls local quality gates and secrets scan', () => {
    const hook = fs.readFileSync(huskyPreCommitPath, 'utf8');
    expect(hook).toContain('pnpm run lint');
    expect(hook).toContain('pnpm run precommit:secrets');
  });

  it('gitleaks configuration file exists', () => {
    expect(fs.existsSync(gitleaksConfigPath)).toBe(true);
  });
});
