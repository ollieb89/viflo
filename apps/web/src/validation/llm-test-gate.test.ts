import { describe, expect, it } from 'vitest';
import { evaluateLlmTestGate } from './llm-test-gate';

describe('evaluateLlmTestGate', () => {
  it('denies by default when opt-in is not set', () => {
    const result = evaluateLlmTestGate({});
    expect(result.allowed).toBe(false);
    expect(result.reason).toContain('disabled by default');
  });

  it('allows opt-in with local profile', () => {
    const result = evaluateLlmTestGate({ runLlmTests: '1', testModelProfile: 'local' });
    expect(result).toEqual({
      allowed: true,
      profile: 'local',
      reason: "LLM-assisted tests allowed with 'local' profile.",
    });
  });

  it('allows opt-in with budget profile', () => {
    const result = evaluateLlmTestGate({ runLlmTests: true, testModelProfile: 'budget' });
    expect(result).toEqual({
      allowed: true,
      profile: 'budget',
      reason: "LLM-assisted tests allowed with 'budget' profile.",
    });
  });

  it('denies opt-in with missing profile', () => {
    const result = evaluateLlmTestGate({ runLlmTests: 'true' });
    expect(result.allowed).toBe(false);
    expect(result.reason).toContain('Invalid TEST_MODEL_PROFILE');
  });

  it('denies unsupported profile values', () => {
    const result = evaluateLlmTestGate({ runLlmTests: '1', testModelProfile: 'premium' });
    expect(result.allowed).toBe(false);
    expect(result.reason).toContain('local');
    expect(result.reason).toContain('budget');
  });
});
