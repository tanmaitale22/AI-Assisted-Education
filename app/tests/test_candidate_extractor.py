import unittest

from app.extractors.candidate_extractor import MemoryCandidate, MemoryCandidateExtractor


class MemoryCandidateExtractorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.extractor = MemoryCandidateExtractor()

    def test_extracts_long_term_memory_sentences(self):
        conversation = (
            "Hello.\n"
            "My name is Tanmai.\n"
            "I am researching Secure Persistent Memory.\n"
            "Today's weather is nice.\n"
            "I prefer VS Code.\n"
            "Thanks."
        )

        candidates = self.extractor.extract(conversation)

        extracted_texts = [candidate.text for candidate in candidates]
        self.assertEqual(extracted_texts, [
            "My name is Tanmai.",
            "I am researching Secure Persistent Memory.",
            "I prefer VS Code.",
        ])

    def test_ignores_greetings_and_small_talk(self):
        conversation = "Hello. Thanks. Okay. Bye. Good Morning. How are you?"
        candidates = self.extractor.extract(conversation)
        self.assertEqual(candidates, [])

    def test_mixed_conversation_keeps_only_memory_candidates(self):
        conversation = (
            "Hi.\n"
            "My project is a secure memory vault.\n"
            "The coffee tastes good.\n"
            "I work as a software engineer.\n"
            "What time is it?"
        )

        candidates = self.extractor.extract(conversation)
        extracted_texts = [candidate.text for candidate in candidates]
        self.assertIn("My project is a secure memory vault.", extracted_texts)
        self.assertIn("I work as a software engineer.", extracted_texts)
        self.assertNotIn("Hi.", extracted_texts)
        self.assertNotIn("The coffee tastes good.", extracted_texts)

    def test_returns_explainable_metadata(self):
        conversation = "My research topic is Secure Persistent Memory."
        candidates = self.extractor.extract(conversation)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].text, "My research topic is Secure Persistent Memory.")
        self.assertTrue(candidates[0].reason)
        self.assertGreaterEqual(candidates[0].combined_score, 0.0)
        self.assertLessEqual(candidates[0].combined_score, 1.0)
        self.assertIsInstance(candidates[0].sentence_index, int)
        self.assertIsInstance(candidates[0].timestamp, str)

    def test_empty_conversation_returns_empty_list(self):
        self.assertEqual(self.extractor.extract("   "), [])


if __name__ == "__main__":
    unittest.main()
