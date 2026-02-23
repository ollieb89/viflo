import { describe, it, expect } from 'vitest';
import { validateSkillFrontmatter, extractTriggers } from './skill';

describe('validateSkillFrontmatter', () => {
  it('validates correct frontmatter', () => {
    const content = `---\nname: test-skill\ndescription: A test skill\ntriggers:\n  - test\n---\n# Content`;
    const result = validateSkillFrontmatter(content);
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  it('fails when frontmatter is missing', () => {
    const content = '# Just markdown\nNo frontmatter here.';
    const result = validateSkillFrontmatter(content);
    expect(result.valid).toBe(false);
    expect(result.errors).toContain('Missing YAML frontmatter');
  });

  it('fails when name is missing', () => {
    const content = `---\ndescription: A test skill\n---\n# Content`;
    const result = validateSkillFrontmatter(content);
    expect(result.valid).toBe(false);
    expect(result.errors).toContain('Missing required field: name');
  });

  it('fails when description is missing', () => {
    const content = `---\nname: test-skill\n---\n# Content`;
    const result = validateSkillFrontmatter(content);
    expect(result.valid).toBe(false);
    expect(result.errors).toContain('Missing required field: description');
  });

  it('fails on invalid YAML', () => {
    const content = `---\nname: : invalid yaml\n---\n# Content`;
    const result = validateSkillFrontmatter(content);
    expect(result.valid).toBe(false);
    expect(result.errors).toContain('Invalid YAML syntax');
  });
});

describe('extractTriggers', () => {
  it('returns triggers from frontmatter', () => {
    const content = `---\nname: test\ndescription: Test\ntriggers:\n  - trigger1\n  - trigger2\n---\nContent`;
    expect(extractTriggers(content)).toEqual(['trigger1', 'trigger2']);
  });

  it('returns empty array when no triggers', () => {
    const content = `---\nname: test\ndescription: Test\n---\nContent`;
    expect(extractTriggers(content)).toEqual([]);
  });

  it('returns empty array when no frontmatter', () => {
    const content = '# Just content';
    expect(extractTriggers(content)).toEqual([]);
  });
});
