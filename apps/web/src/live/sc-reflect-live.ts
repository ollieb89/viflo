import { existsSync, readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';

const REQUIRED_FILES = [
  'prompts/sc-reflect.md',
  'prompts/sc-reflect.toml',
  'commands/sg/reflect.md',
  'INDEX.md',
] as const;

const REQUIRED_MARKERS: Record<(typeof REQUIRED_FILES)[number], string[]> = {
  'prompts/sc-reflect.md': ['/sc:reflect', 'Task Reflection and Validation'],
  'prompts/sc-reflect.toml': ['name = "sc-reflect"', 'command = "/sc:reflect"'],
  'commands/sg/reflect.md': ['/sc:reflect', 'Serena'],
  'INDEX.md': ['/sc:reflect', 'prompts/sc-reflect.md', 'commands/sg/reflect.md'],
};

export interface LiveValidationResult {
  missing: string[];
  markerFailures: string[];
  isValid: boolean;
}

export function getRepositoryRoot(startDir: string = process.cwd()): string {
  let current = resolve(startDir);

  for (;;) {
    const hasSignals = REQUIRED_FILES.every((relPath) => existsSync(join(current, relPath)));
    if (hasSignals) {
      return current;
    }

    const parent = dirname(current);
    if (parent === current) {
      throw new Error(`Repository root not found from start dir: ${startDir}`);
    }
    current = parent;
  }
}

export function validateScReflectArtifacts(repoRoot: string): LiveValidationResult {
  const missing: string[] = [];
  const markerFailures: string[] = [];

  for (const relPath of REQUIRED_FILES) {
    const absolutePath = join(repoRoot, relPath);
    if (!existsSync(absolutePath)) {
      missing.push(relPath);
      continue;
    }

    const content = readFileSync(absolutePath, 'utf8');
    for (const marker of REQUIRED_MARKERS[relPath]) {
      if (!content.includes(marker)) {
        markerFailures.push(`${relPath}: missing marker \"${marker}\"`);
      }
    }
  }

  return {
    missing,
    markerFailures,
    isValid: missing.length === 0 && markerFailures.length === 0,
  };
}
