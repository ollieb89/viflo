import Anthropic from '@anthropic-ai/sdk';
import * as fs from 'fs';
import * as path from 'path';

const client = new Anthropic(); // reads ANTHROPIC_API_KEY from env

interface TestCase {
  filePath: string;
  pattern: string;
  model: string;
  inputPrompt: string;
  expectedCriteria: string[];
}

function parseTestCase(filePath: string): TestCase {
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n');

  // Parse frontmatter
  let pattern = '';
  let model = 'claude-sonnet-4-6';
  let inFrontmatter = false;
  let frontmatterDone = false;
  let i = 0;

  if (lines[0] === '---') {
    inFrontmatter = true;
    i = 1;
  }
  for (; i < lines.length && !frontmatterDone; i++) {
    if (lines[i] === '---') { frontmatterDone = true; continue; }
    if (inFrontmatter) {
      const [key, ...rest] = lines[i].split(':');
      if (key.trim() === 'pattern') pattern = rest.join(':').trim();
      if (key.trim() === 'model') model = rest.join(':').trim();
    }
  }

  // Extract Input Prompt section
  const inputStart = content.indexOf('## Input Prompt\n');
  const criteriaStart = content.indexOf('## Expected Output Criteria\n');
  const inputPrompt = content.slice(inputStart + '## Input Prompt\n'.length, criteriaStart).trim();

  // Extract criteria bullets
  const criteriaSection = content.slice(criteriaStart + '## Expected Output Criteria\n'.length).trim();
  const expectedCriteria = criteriaSection
    .split('\n')
    .filter((l) => l.startsWith('- '))
    .map((l) => l.slice(2).trim());

  return { filePath, pattern, model, inputPrompt, expectedCriteria };
}

async function runTestCase(testCase: TestCase): Promise<{ passed: boolean; reason: string }> {
  // Build messages from Input Prompt section
  const lines = testCase.inputPrompt.split('\n');
  let system = '';
  let userContent = '';

  for (const line of lines) {
    if (line.startsWith('System: ')) system = line.slice('System: '.length);
    else if (line.startsWith('User: ') || line.startsWith('User (real): ')) {
      userContent = line.replace(/^User \(real\): /, '').replace(/^User: /, '');
    } else if (userContent) {
      userContent += '\n' + line;
    }
  }

  const messages: Anthropic.MessageParam[] = [{ role: 'user', content: userContent.trim() }];
  const createParams: Anthropic.MessageCreateParamsNonStreaming = {
    model: testCase.model,
    max_tokens: 1024,
    messages,
  };
  if (system) createParams.system = system;

  const response = await client.messages.create(createParams);
  const output = response.content[0].type === 'text' ? response.content[0].text : '';

  // LLM-as-judge using cheap model
  const judgeResponse = await client.messages.create({
    model: 'claude-haiku-4-5-20251001',
    max_tokens: 256,
    messages: [{
      role: 'user',
      content: `Output to evaluate:\n"${output}"\n\nCriteria (ALL must be satisfied):\n${testCase.expectedCriteria.map((c, i) => `${i + 1}. ${c}`).join('\n')}\n\nDoes the output satisfy ALL criteria? Reply with exactly PASS or FAIL on the first line, then one sentence explaining why.`,
    }],
  });

  const verdict = judgeResponse.content[0].type === 'text' ? judgeResponse.content[0].text.trim() : 'FAIL';
  const passed = verdict.toUpperCase().startsWith('PASS');
  const reason = verdict.split('\n').slice(1).join(' ').trim() || verdict;

  return { passed, reason };
}

async function main() {
  const goldenSetDir = path.dirname(__filename);
  const testFiles = fs.readdirSync(goldenSetDir)
    .filter((f) => f.endsWith('.md'))
    .map((f) => path.join(goldenSetDir, f));

  if (testFiles.length === 0) {
    console.error('No .md test case files found in golden-set/');
    process.exit(1);
  }

  let failures = 0;

  for (const filePath of testFiles) {
    const testCase = parseTestCase(filePath);
    process.stdout.write(`  Running ${testCase.pattern}... `);
    try {
      const result = await runTestCase(testCase);
      if (result.passed) {
        console.log(`✓ PASS`);
      } else {
        console.log(`✗ FAIL — ${result.reason}`);
        failures++;
      }
    } catch (err) {
      console.log(`✗ ERROR — ${(err as Error).message}`);
      failures++;
    }
  }

  console.log(`\n${testFiles.length - failures}/${testFiles.length} passed`);
  if (failures > 0) process.exit(1);
}

main();
