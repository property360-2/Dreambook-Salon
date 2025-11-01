import { prisma } from '../../lib/prisma.js';
import { env } from '../../config/env.js';
import { logger } from '../../config/logger.js';

const DEFAULT_FALLBACK_REPLY =
  "I'm not sure how to help with that yet, but a team member will follow up soon.";
const SESSION_THROTTLE_MS = env.chatbotRateLimitMs ?? 800;
const MAX_TRACKED_SESSIONS = 500;

const sessionTimestamps = new Map();

function pruneSessions() {
  if (sessionTimestamps.size <= MAX_TRACKED_SESSIONS) {
    return;
  }

  const sortedKeys = Array.from(sessionTimestamps.entries()).sort(
    (a, b) => a[1] - b[1],
  );

  while (sortedKeys.length > MAX_TRACKED_SESSIONS) {
    const [key] = sortedKeys.shift();
    sessionTimestamps.delete(key);
  }
}

function checkThrottle(sessionKey) {
  const now = Date.now();
  const lastMessageAt = sessionTimestamps.get(sessionKey);

  if (lastMessageAt && now - lastMessageAt < SESSION_THROTTLE_MS) {
    return SESSION_THROTTLE_MS - (now - lastMessageAt);
  }

  sessionTimestamps.set(sessionKey, now);
  pruneSessions();
  return 0;
}

function normalizeMessage(value) {
  return value.toLowerCase();
}

function toRuleResource(rule) {
  return {
    id: rule.id,
    pattern: rule.pattern,
    reply: rule.reply,
    priority: rule.priority,
    isActive: rule.isActive,
    createdAt: rule.createdAt,
    updatedAt: rule.updatedAt,
  };
}

export async function listChatbotRules() {
  const rules = await prisma.chatbotRule.findMany({
    orderBy: [
      { priority: 'desc' },
      { createdAt: 'asc' },
    ],
  });

  return rules.map(toRuleResource);
}

export async function createChatbotRule(data, actor) {
  const rule = await prisma.chatbotRule.create({
    data: {
      pattern: data.pattern.trim(),
      reply: data.reply.trim(),
      priority: data.priority ?? 0,
      isActive: data.isActive ?? true,
      createdById: actor?.id ?? null,
    },
  });

  logger.info(
    {
      ruleId: rule.id,
      pattern: rule.pattern,
    },
    'Chatbot rule created',
  );

  return toRuleResource(rule);
}

export async function updateChatbotRule(id, data) {
  const rule = await prisma.chatbotRule.update({
    where: { id },
    data: {
      ...(data.pattern !== undefined ? { pattern: data.pattern.trim() } : {}),
      ...(data.reply !== undefined ? { reply: data.reply.trim() } : {}),
      ...(data.priority !== undefined ? { priority: data.priority } : {}),
      ...(data.isActive !== undefined ? { isActive: data.isActive } : {}),
    },
  });

  logger.info(
    {
      ruleId: rule.id,
      pattern: rule.pattern,
    },
    'Chatbot rule updated',
  );

  return toRuleResource(rule);
}

export async function deleteChatbotRule(id) {
  await prisma.chatbotRule.delete({
    where: { id },
  });
}

export async function respondToMessage(message, sessionId) {
  const sessionKey = sessionId ?? 'anonymous';
  const retryAfter = checkThrottle(sessionKey);

  if (retryAfter > 0) {
    return {
      reply: 'Hang tight — one message at a time! Try again in a moment.',
      throttled: true,
      retryAfterMs: retryAfter,
      matchedRuleId: null,
    };
  }

  const normalizedMessage = normalizeMessage(message);

  const rules = await prisma.chatbotRule.findMany({
    where: {
      isActive: true,
    },
    orderBy: [
      { priority: 'desc' },
      { createdAt: 'asc' },
    ],
  });

  const matched = rules.find((rule) =>
    normalizedMessage.includes(rule.pattern.toLowerCase()),
  );

  if (matched) {
    logger.debug(
      {
        ruleId: matched.id,
        pattern: matched.pattern,
      },
      'Chatbot rule matched',
    );

    return {
      reply: matched.reply,
      throttled: false,
      retryAfterMs: 0,
      matchedRuleId: matched.id,
    };
  }

  const fallback = env.chatbotFallbackReply ?? DEFAULT_FALLBACK_REPLY;

  return {
    reply: fallback,
    throttled: false,
    retryAfterMs: 0,
    matchedRuleId: null,
  };
}
