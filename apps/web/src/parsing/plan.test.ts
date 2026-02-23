import { describe, it, expect } from 'vitest';
import { parsePlanFile, countTasksByType } from './plan';

describe('parsePlanFile', () => {
  it('parses plan with frontmatter and tasks', () => {
    const content = `---\nphase: 5\nplan: 1\n---\n<plan>\n<task type="auto" priority="1">\n  <name>Task 1</name>\n</task>\n<task type="manual">\n  <name>Task 2</name>\n</task>\n</plan>`;

    const result = parsePlanFile(content);
    expect(result.phase).toBe(5);
    expect(result.plan).toBe(1);
    expect(result.tasks).toHaveLength(2);
    expect(result.tasks[0].name).toBe('Task 1');
    expect(result.tasks[0].type).toBe('auto');
    expect(result.tasks[0].priority).toBe(1);
  });

  it('returns empty tasks when no tasks found', () => {
    const content = `---\nphase: 1\n---\n<plan>\n</plan>`;
    const result = parsePlanFile(content);
    expect(result.tasks).toHaveLength(0);
  });

  it('defaults to auto type when not specified', () => {
    const content = `<task>\n  <name>Task</name>\n</task>`;
    const result = parsePlanFile(content);
    expect(result.tasks[0].type).toBe('auto');
  });
});

describe('countTasksByType', () => {
  it('counts tasks by type correctly', () => {
    const tasks = [
      { type: 'auto' as const, name: 'Auto 1' },
      { type: 'auto' as const, name: 'Auto 2' },
      { type: 'manual' as const, name: 'Manual 1' },
    ];
    const result = countTasksByType(tasks);
    expect(result.auto).toBe(2);
    expect(result.manual).toBe(1);
  });

  it('returns zero counts for empty array', () => {
    const result = countTasksByType([]);
    expect(result.auto).toBe(0);
    expect(result.manual).toBe(0);
  });
});
