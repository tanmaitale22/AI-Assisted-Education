import unittest

from memory import AdaptiveMemoryExtractor, MemoryValidator, MemoryRecord


class AMEEExtractorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = MemoryValidator()
        self.extractor = AdaptiveMemoryExtractor(validator=self.validator)

    def test_extracts_learning_goal(self):
        memories = self.extractor.extract("I am preparing for GATE.")
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0].category, "learning_goal")
        self.assertIn("GATE", memories[0].content)

    def test_extracts_academic_progress(self):
        memories = self.extractor.extract("I finished CNN yesterday.")
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0].category, "academic_progress")
        self.assertIn("CNN", memories[0].content)

    def test_extracts_weak_topic(self):
        memories = self.extractor.extract("I still don't understand Dynamic Programming.")
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0].category, "weak_topic")
        self.assertIn("Dynamic Programming", memories[0].content)

    def test_extracts_strong_topic(self):
        memories = self.extractor.extract("I am good at Python.")
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0].category, "strong_topic")
        self.assertIn("Python", memories[0].content)

    def test_extracts_learning_preference(self):
        memories = self.extractor.extract("I prefer diagrams and simple explanations.")
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0].category, "learning_preference")
        self.assertIn("diagram", memories[0].content.lower())

    def test_extracts_important_date(self):
        memories = self.extractor.extract("My exam is next Friday.")
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0].category, "important_date")
        self.assertIn("exam", memories[0].content.lower())

    def test_extracts_personal_context(self):
        memories = self.extractor.extract("I am a Computer Engineering student in semester 6.")
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0].category, "personal_context")
        self.assertIn("Computer Engineering", memories[0].content)

    def test_extracts_multiple_memories(self):
        memories = self.extractor.extract(
            "I have my AI exam next Monday and I still don't understand CNN. Please explain using diagrams."
        )
        categories = [item.category for item in memories]
        self.assertIn("learning_goal", categories)
        self.assertIn("weak_topic", categories)
        self.assertIn("learning_preference", categories)

    def test_ignores_greetings_and_small_talk(self):
        memories = self.extractor.extract("Thanks! Hi there.")
        self.assertEqual(memories, [])

    def test_ignores_random_questions(self):
        memories = self.extractor.extract("Can you explain CNN?")
        self.assertEqual(memories, [])

    def test_ignores_one_time_requests(self):
        memories = self.extractor.extract("Please explain backpropagation briefly.")
        self.assertEqual(memories, [])

    def test_ignores_general_ai_responses(self):
        memories = self.extractor.extract("I can help you with that.")
        self.assertEqual(memories, [])

    def test_empty_message_returns_empty_list(self):
        self.assertEqual(self.extractor.extract("   "), [])

    def test_validator_rejects_empty_content(self):
        invalid = [{"category": "weak_topic", "content": "   ", "confidence": 0.95}]
        self.assertEqual(self.validator.validate(invalid), [])

    def test_validator_rejects_invalid_category(self):
        invalid = [{"category": "random_category", "content": "Python", "confidence": 0.95}]
        self.assertEqual(self.validator.validate(invalid), [])

    def test_validator_rejects_confidence_out_of_range(self):
        invalid = [{"category": "strong_topic", "content": "Python", "confidence": 1.2}]
        self.assertEqual(self.validator.validate(invalid), [])

    def test_validator_rejects_duplicate_memories(self):
        duplicates = [
            MemoryRecord(category="weak_topic", content="Dynamic Programming", confidence=0.95),
            MemoryRecord(category="weak_topic", content="Dynamic Programming", confidence=0.97),
        ]
        self.assertEqual(len(self.validator.validate(duplicates)), 1)

    def test_validator_normalizes_preference_text(self):
        normalized = self.validator.validate([
            MemoryRecord(category="learning_preference", content="likes diagrams", confidence=0.93)
        ])
        self.assertEqual(normalized[0].content, "Prefers diagram-based explanations")

    def test_validator_normalizes_topic_text(self):
        normalized = self.validator.validate([
            MemoryRecord(category="weak_topic", content="doesn't understand recursion", confidence=0.95)
        ])
        self.assertEqual(normalized[0].content, "Recursion")

    def test_validator_normalizes_goal_text(self):
        normalized = self.validator.validate([
            MemoryRecord(category="learning_goal", content="prepare for gate", confidence=0.94)
        ])
        self.assertEqual(normalized[0].content, "Preparing for GATE")

    def test_validator_rounds_confidence(self):
        normalized = self.validator.validate([
            MemoryRecord(category="strong_topic", content="SQL", confidence=0.987)
        ])
        self.assertEqual(normalized[0].confidence, 0.99)

    def test_validator_accepts_valid_record(self):
        normalized = self.validator.validate([
            MemoryRecord(category="important_date", content="Assignment due tomorrow", confidence=0.9)
        ])
        self.assertEqual(len(normalized), 1)
        self.assertEqual(normalized[0].category, "important_date")

    def test_rule_based_extractor_is_available(self):
        from memory.extractor import RuleBasedMemoryExtractor

        extractor = RuleBasedMemoryExtractor()
        memories = extractor.extract("I am comfortable with SQL.")
        self.assertEqual(memories[0].category, "strong_topic")

    def test_llm_response_parser_handles_invalid_json(self):
        from memory.extractor import GeminiMemoryExtractor

        extractor = GeminiMemoryExtractor(validator=self.validator, api_key=None)
        parsed = extractor._parse_response("not json")
        self.assertEqual(parsed, [])

    def test_llm_response_parser_handles_markdown_json(self):
        from memory.extractor import GeminiMemoryExtractor

        extractor = GeminiMemoryExtractor(validator=self.validator, api_key=None)
        parsed = extractor._parse_response("```json\n[{\"category\": \"weak_topic\", \"content\": \"CNN\", \"confidence\": 0.98}]\n```")
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["category"], "weak_topic")

    def test_non_educational_personal_detail_is_ignored(self):
        memories = self.extractor.extract("I love hiking on weekends.")
        self.assertEqual(memories, [])

    def test_ignores_temporary_small_talk(self):
        memories = self.extractor.extract("Okay, sounds good.")
        self.assertEqual(memories, [])

    def test_ignores_general_request_about_current_topic(self):
        memories = self.extractor.extract("Explain neural networks in simple terms.")
        self.assertEqual(memories, [])

    def test_does_not_hallucinate_memories(self):
        memories = self.extractor.extract("What is supervised learning?")
        self.assertEqual(memories, [])

    def test_handles_mixed_case_categories(self):
        normalized = self.validator.validate([
            MemoryRecord(category="Learning_Goal", content="Machine Learning", confidence=0.91)
        ])
        self.assertEqual(normalized[0].category, "learning_goal")

    def test_handles_whitespace_and_punctuation(self):
        normalized = self.validator.validate([
            MemoryRecord(category=" learning_preference ", content="  likes diagrams  ", confidence=0.93)
        ])
        self.assertEqual(normalized[0].content, "Prefers diagram-based explanations")

    def test_supports_multiple_distinct_memories_in_one_message(self):
        memories = self.extractor.extract("I learned backpropagation and I prefer code examples for SQL.")
        categories = {item.category for item in memories}
        self.assertTrue(categories.issuperset({"academic_progress", "learning_preference"}))

    def test_extracts_important_date_with_due_date(self):
        memories = self.extractor.extract("Assignment is due tomorrow.")
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0].category, "important_date")


if __name__ == "__main__":
    unittest.main()
