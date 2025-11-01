import { afterEach, beforeEach, describe, expect, test, jest } from '@jest/globals';

const loadService = async (rules) => {
  const mockFindMany = jest.fn().mockResolvedValue(rules);

  jest.unstable_mockModule('../../lib/prisma.js', () => ({
    prisma: {
      chatbotRule: {
        findMany: mockFindMany,
      },
    },
  }));

  const module = await import('./chatbot.service.js');

  return { respondToMessage: module.respondToMessage, mockFindMany };
};

beforeEach(() => {
  jest.resetModules();
  process.env.SALON_CHATBOT_FALLBACK_REPLY = 'Let me check with the team for you.';
  process.env.SALON_CHATBOT_RATE_LIMIT = '200';
});

afterEach(() => {
  delete process.env.SALON_CHATBOT_FALLBACK_REPLY;
  delete process.env.SALON_CHATBOT_RATE_LIMIT;
});

describe('chatbot.service respondToMessage', () => {
  test('returns the highest priority matching rule', async () => {
    const { respondToMessage, mockFindMany } = await loadService([
      {
        id: 'rule_1',
        pattern: 'hello',
        reply: 'Hello! Need help booking?',
        priority: 50,
        isActive: true,
      },
      {
        id: 'rule_2',
        pattern: 'hours',
        reply: 'We are open 9am - 6pm daily.',
        priority: 10,
        isActive: true,
      },
    ]);

    const response = await respondToMessage('Hello there!', 'session-a');

    expect(mockFindMany).toHaveBeenCalled();
    expect(response).toMatchObject({
      throttled: false,
      reply: 'Hello! Need help booking?',
      matchedRuleId: 'rule_1',
    });
  });

  test('falls back when no rule matches', async () => {
    const { respondToMessage } = await loadService([]);

    const response = await respondToMessage('Do you offer facials?', 'session-b');

    expect(response).toMatchObject({
      throttled: false,
      matchedRuleId: null,
      reply: 'Let me check with the team for you.',
    });
  });

  test('throttles rapid messages per session', async () => {
    const { respondToMessage } = await loadService([
      {
        id: 'rule_1',
        pattern: 'price',
        reply: 'Service prices start at $25.',
        priority: 30,
        isActive: true,
      },
    ]);

    const first = await respondToMessage('Price list please', 'session-c');
    const second = await respondToMessage('Price list please', 'session-c');

    expect(first.throttled).toBe(false);
    expect(second.throttled).toBe(true);
    expect(second.retryAfterMs).toBeGreaterThan(0);
  });
});
