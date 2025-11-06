import json

from django.test import TestCase
from django.urls import reverse

from chatbot.models import Rule


class RuleModelTests(TestCase):
    def test_rule_creation(self):
        rule = Rule.objects.create(
            keyword="appointment",
            response="You can book an appointment on our website.",
            priority=10,
        )
        self.assertEqual(rule.keyword, "appointment")
        self.assertTrue(rule.is_active)

    def test_matches_method_case_insensitive(self):
        rule = Rule.objects.create(
            keyword="booking",
            response="Visit our booking page.",
        )

        self.assertTrue(rule.matches("I want to make a BOOKING"))
        self.assertTrue(rule.matches("booking information"))
        self.assertTrue(rule.matches("How do I make a Booking?"))

    def test_matches_method_no_match(self):
        rule = Rule.objects.create(
            keyword="appointment",
            response="You can book an appointment on our website.",
        )

        self.assertFalse(rule.matches("Tell me about services"))
        self.assertFalse(rule.matches("What are your hours?"))


class ChatbotInterfaceViewTests(TestCase):
    def test_chatbot_interface_view_accessible(self):
        response = self.client.get(reverse("chatbot:interface"))
        self.assertEqual(response.status_code, 200)


class ChatbotAPITests(TestCase):
    def setUp(self):
        self.rule1 = Rule.objects.create(
            keyword="hours",
            response="We are open from 9 AM to 6 PM.",
            priority=10,
        )
        self.rule2 = Rule.objects.create(
            keyword="appointment",
            response="You can book an appointment on our website.",
            priority=5,
        )

    def test_chatbot_respond_api(self):
        response = self.client.post(
            "/api/chatbot/respond/",
            data=json.dumps({"message": "What are your hours?"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["response"], self.rule1.response)

    def test_chatbot_priority_matching(self):
        # Higher priority rule should match first
        response = self.client.post(
            "/api/chatbot/respond/",
            data=json.dumps({"message": "What are your hours for appointments?"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # Should match hours (priority 10) before appointment (priority 5)
        self.assertEqual(data["response"], self.rule1.response)

    def test_chatbot_default_response(self):
        response = self.client.post(
            "/api/chatbot/respond/",
            data=json.dumps({"message": "Something completely unrelated"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("not sure", data["response"])

    def test_chatbot_inactive_rule_not_matched(self):
        self.rule1.is_active = False
        self.rule1.save()

        response = self.client.post(
            "/api/chatbot/respond/",
            data=json.dumps({"message": "What are your hours?"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # Should not match inactive rule
        self.assertNotEqual(data["response"], self.rule1.response)
