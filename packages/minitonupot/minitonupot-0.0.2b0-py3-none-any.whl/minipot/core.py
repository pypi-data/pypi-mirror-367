class MiniNeuralEngine:
    def __init__(self, name: str, performance_score: float = 1.0):
        self.name = name
        self.performance_score = performance_score
        self.boosted = False

    def __repr__(self):
        return f"<MiniNeuralEngine name={self.name}, score={self.performance_score:.2f}, boosted={self.boosted}>"

    def reset(self):
        self.performance_score = 1.0
        self.boosted = False
