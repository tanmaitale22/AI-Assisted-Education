from memory.memory_engine import MemoryEngine


memory = MemoryEngine()

memory.remember(
    "What is supervised learning?",
    "Supervised learning uses labelled training data."
)

memory.remember(
    "What is classification?",
    "Classification is a supervised learning task where outputs are categories."
)

memories = memory.get_memory()

print("\nSTUDENT MEMORY:\n")

for memory_item in memories:
    print(memory_item)