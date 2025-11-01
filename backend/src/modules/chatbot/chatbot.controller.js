import {
  chatbotMessageSchema,
  createChatbotRuleSchema,
  updateChatbotRuleSchema,
} from './chatbot.schema.js';
import {
  createChatbotRule,
  deleteChatbotRule,
  listChatbotRules,
  respondToMessage,
  updateChatbotRule,
} from './chatbot.service.js';

export async function getChatbotRules(_req, res, next) {
  try {
    const rules = await listChatbotRules();
    res.json({ rules });
  } catch (error) {
    next(error);
  }
}

export async function postChatbotRule(req, res, next) {
  try {
    const payload = createChatbotRuleSchema.parse(req.body);
    const rule = await createChatbotRule(payload, req.user);
    res.status(201).json({ rule });
  } catch (error) {
    if (error.name === 'ZodError') {
      error.status = 400;
      error.message = error.errors?.[0]?.message ?? 'Invalid request payload';
    }
    next(error);
  }
}

export async function putChatbotRule(req, res, next) {
  try {
    const payload = updateChatbotRuleSchema.parse(req.body);
    const rule = await updateChatbotRule(req.params.id, payload);
    res.json({ rule });
  } catch (error) {
    if (error.name === 'ZodError') {
      error.status = 400;
      error.message = error.errors?.[0]?.message ?? 'Invalid request payload';
    }
    if (error.code === 'P2025' && !error.status) {
      error.status = 404;
      error.message = 'Chatbot rule not found';
    }
    next(error);
  }
}

export async function deleteChatbotRuleHandler(req, res, next) {
  try {
    await deleteChatbotRule(req.params.id);
    res.status(204).send();
  } catch (error) {
    if (error.code === 'P2025' && !error.status) {
      error.status = 404;
      error.message = 'Chatbot rule not found';
    }
    next(error);
  }
}

export async function postChatbotResponse(req, res, next) {
  try {
    const payload = chatbotMessageSchema.parse(req.body);
    const response = await respondToMessage(payload.message, payload.sessionId ?? req.ip);
    res.json(response);
  } catch (error) {
    if (error.name === 'ZodError') {
      error.status = 400;
      error.message = error.errors?.[0]?.message ?? 'Invalid request payload';
    }
    next(error);
  }
}
