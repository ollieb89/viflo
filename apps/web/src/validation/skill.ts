import YAML from 'yaml';

export interface SkillFrontmatter {
  name: string;
  description: string;
  triggers?: string[];
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

export function validateSkillFrontmatter(content: string): ValidationResult {
  const errors: string[] = [];

  // Extract frontmatter between --- markers
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) {
    return { valid: false, errors: ['Missing YAML frontmatter'] };
  }

  try {
    const frontmatter = YAML.parse(match[1]) as SkillFrontmatter;

    if (!frontmatter.name) {
      errors.push('Missing required field: name');
    }
    if (!frontmatter.description) {
      errors.push('Missing required field: description');
    }

    return { valid: errors.length === 0, errors };
  } catch (e) {
    return { valid: false, errors: ['Invalid YAML syntax'] };
  }
}

export function extractTriggers(content: string): string[] {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return [];

  try {
    const frontmatter = YAML.parse(match[1]) as SkillFrontmatter;
    return frontmatter.triggers || [];
  } catch {
    return [];
  }
}
