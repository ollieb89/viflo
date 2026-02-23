export interface Task {
  type: 'auto' | 'manual';
  name: string;
  priority?: number;
}

export interface ParsedPlan {
  phase: number;
  plan: number;
  tasks: Task[];
}

export function parsePlanFile(content: string): ParsedPlan {
  // Extract phase and plan from frontmatter
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
  let phase = 0;
  let planNum = 0;

  if (frontmatterMatch) {
    const phaseMatch = frontmatterMatch[1].match(/phase:\s*(\d+)/);
    const planMatch = frontmatterMatch[1].match(/plan:\s*(\d+)/);
    if (phaseMatch) phase = parseInt(phaseMatch[1], 10);
    if (planMatch) planNum = parseInt(planMatch[1], 10);
  }

  // Extract tasks from XML-like structure
  const tasks: Task[] = [];
  const taskRegex = /<task[^>]*>[\s\S]*?<\/task>/g;
  const taskMatches = content.matchAll(taskRegex);

  for (const match of taskMatches) {
    const taskContent = match[0];
    const typeMatch = taskContent.match(/type="(auto|manual)"/);
    const nameMatch = taskContent.match(/<name>([\s\S]*?)<\/name>/);
    const priorityMatch = taskContent.match(/priority="(\d+)"/);

    if (nameMatch) {
      tasks.push({
        type: (typeMatch?.[1] as 'auto' | 'manual') || 'auto',
        name: nameMatch[1].trim(),
        priority: priorityMatch ? parseInt(priorityMatch[1], 10) : undefined,
      });
    }
  }

  return { phase, plan: planNum, tasks };
}

export function countTasksByType(tasks: Task[]): { auto: number; manual: number } {
  return tasks.reduce(
    (acc, task) => {
      acc[task.type]++;
      return acc;
    },
    { auto: 0, manual: 0 }
  );
}
