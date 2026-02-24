'use strict';
const fs = require('fs');
const path = require('path');

let tmpDir;
beforeEach(() => {
  vi.resetModules();
  tmpDir = fs.mkdtempSync(path.join('/tmp', 'viflo-skills-test-'));
});
afterEach(() => {
  fs.rmSync(tmpDir, { recursive: true, force: true });
  vi.restoreAllMocks();
});

describe('scanSkills', () => {
  it('returns empty array when .agent/skills/ does not exist', () => {
    const { scanSkills } = require('../skills.cjs');
    const result = scanSkills(tmpDir);
    expect(result).toEqual([]);
  });

  it('returns empty array when skills dir exists but has no subdirectories', () => {
    const { scanSkills } = require('../skills.cjs');
    fs.mkdirSync(path.join(tmpDir, '.agent', 'skills'), { recursive: true });
    const result = scanSkills(tmpDir);
    expect(result).toEqual([]);
  });

  it('returns one @-import line for a single skill directory', () => {
    const { scanSkills } = require('../skills.cjs');
    fs.mkdirSync(path.join(tmpDir, '.agent', 'skills', 'my-skill'), { recursive: true });
    const result = scanSkills(tmpDir);
    expect(result).toEqual([`@${tmpDir}/.agent/skills/my-skill/SKILL.md`]);
  });

  it('returns multiple @-import lines sorted alphabetically for multiple skill dirs', () => {
    const { scanSkills } = require('../skills.cjs');
    fs.mkdirSync(path.join(tmpDir, '.agent', 'skills', 'zebra-skill'), { recursive: true });
    fs.mkdirSync(path.join(tmpDir, '.agent', 'skills', 'alpha-skill'), { recursive: true });
    fs.mkdirSync(path.join(tmpDir, '.agent', 'skills', 'middle-skill'), { recursive: true });
    const result = scanSkills(tmpDir);
    expect(result).toEqual([
      `@${tmpDir}/.agent/skills/alpha-skill/SKILL.md`,
      `@${tmpDir}/.agent/skills/middle-skill/SKILL.md`,
      `@${tmpDir}/.agent/skills/zebra-skill/SKILL.md`,
    ]);
  });

  it('ignores files (non-directories) inside .agent/skills/', () => {
    const { scanSkills } = require('../skills.cjs');
    fs.mkdirSync(path.join(tmpDir, '.agent', 'skills', 'real-skill'), { recursive: true });
    fs.writeFileSync(path.join(tmpDir, '.agent', 'skills', 'a-file.md'), 'not a skill dir');
    const result = scanSkills(tmpDir);
    expect(result).toEqual([`@${tmpDir}/.agent/skills/real-skill/SKILL.md`]);
  });
});
