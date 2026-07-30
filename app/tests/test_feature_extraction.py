import unittest

from app.scoring.feature_extractor import FeatureExtractor
from app.extractors.candidate_extractor import RegexMemoryCandidateExtractor
from app.scoring.importance_engine import ImportanceScoringEngine
from app.scoring.decision_engine import DecisionEngine


class FeatureExtractionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.extractor = RegexMemoryCandidateExtractor()
        self.feature_extractor = FeatureExtractor()
        self.scoring_engine = ImportanceScoringEngine(weight_config={
            "preference": 0.05,
            "long_term": 0.40,
            "frequency": 0.05,
            "task": 0.25,
            "confidence": 0.15,
            "recency": 0.10,
        }, thresholds={"permanent": 0.80, "temporary": 0.50})
        self.decision_engine = DecisionEngine(thresholds={"permanent": 0.80, "temporary": 0.50})

    def test_candidate_extractor_ignores_greetings(self):
        text = "Hello. Thanks. My favorite language is Python."
        candidates = self.extractor.extract(text)
        self.assertEqual(len(candidates), 1)
        self.assertIn("favorite language is Python", candidates[0])

    def test_feature_extractor_marks_preference(self):
        features = self.feature_extractor.extract_features(
            "My favorite language is Python.",
            agent_profile="Research Assistant",
            history=[]
        )
        self.assertGreater(features.preference, 0.7)
        self.assertGreater(features.long_term, 0.6)

    def test_scoring_engine_and_decision(self):
        text = "My favorite language is Python and I work as a software engineer."
        features = self.feature_extractor.extract_features(text, agent_profile="Coding Assistant", history=[])
        score = self.scoring_engine.score(features)
        decision = self.decision_engine.decide(score)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        self.assertIn(decision, {"PERMANENT_MEMORY", "TEMPORARY_MEMORY", "DISCARD"})

    def test_professional_memory_should_not_be_discarded(self):
        text = "I work as a software engineer."
        features = self.feature_extractor.extract_features(text, agent_profile="Coding Assistant", history=[])
        score = self.scoring_engine.score(features)
        decision = self.decision_engine.decide(score)
        self.assertGreaterEqual(score, 0.5)
        self.assertNotEqual(decision, "DISCARD")


if __name__ == "__main__":
    unittest.main()
