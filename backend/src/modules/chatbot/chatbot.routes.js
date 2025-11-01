import { Router } from 'express';

import { requireAuth, requireRoles } from '../../middleware/auth.js';
import {
  deleteChatbotRuleHandler,
  getChatbotRules,
  postChatbotResponse,
  postChatbotRule,
  putChatbotRule,
} from './chatbot.controller.js';

export const chatbotRouter = Router();

chatbotRouter.get('/rules', requireAuth, requireRoles('ADMIN', 'STAFF'), getChatbotRules);
chatbotRouter.post('/rules', requireAuth, requireRoles('ADMIN'), postChatbotRule);
chatbotRouter.put('/rules/:id', requireAuth, requireRoles('ADMIN'), putChatbotRule);
chatbotRouter.delete(
  '/rules/:id',
  requireAuth,
  requireRoles('ADMIN'),
  deleteChatbotRuleHandler,
);

chatbotRouter.post('/respond', postChatbotResponse);
