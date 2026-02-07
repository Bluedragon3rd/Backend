class SituationVector:
    def __init__(self, identifier):
        self.id = identifier
        self.severity = 0
        self.specificity = 0
        self.verifiability = 0
        self.frequency = 0
        self.truth_plausibility = 0
        self.fatigue = 0
        self.memory_load = 0