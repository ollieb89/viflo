export type LlmTestProfile = 'local' | 'budget';

export interface LlmTestGateInput {
  runLlmTests?: string | boolean;
  testModelProfile?: string | null;
}

export interface LlmTestGateDecision {
  allowed: boolean;
  reason: string;
  profile?: LlmTestProfile;
}

function isOptInEnabled(value: string | boolean | undefined): boolean {
  if (typeof value === 'boolean') {
    return value;
  }

  if (typeof value !== 'string') {
    return false;
  }

  const normalized = value.trim().toLowerCase();
  return normalized === '1' || normalized === 'true' || normalized === 'yes';
}

export function evaluateLlmTestGate(input: LlmTestGateInput): LlmTestGateDecision {
  const enabled = isOptInEnabled(input.runLlmTests);

  if (!enabled) {
    return {
      allowed: false,
      reason: 'LLM-assisted tests are disabled by default. Set RUN_LLM_TESTS=1 to opt in.',
    };
  }

  const profile = (input.testModelProfile ?? '').trim().toLowerCase();
  if (profile === 'local' || profile === 'budget') {
    return {
      allowed: true,
      profile,
      reason: `LLM-assisted tests allowed with '${profile}' profile.`,
    };
  }

  return {
    allowed: false,
    reason: "Invalid TEST_MODEL_PROFILE. Allowed values: 'local' or 'budget'.",
  };
}
