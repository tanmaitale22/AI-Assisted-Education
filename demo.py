from memory import AdaptiveMemoryExtractor

extractor = AdaptiveMemoryExtractor()
memories = extractor.extract("I have my AI exam next Monday and I still don't understand CNN.")
print(memories)