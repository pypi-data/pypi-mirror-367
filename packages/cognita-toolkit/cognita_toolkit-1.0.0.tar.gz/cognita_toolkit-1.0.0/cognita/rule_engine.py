class RuleEngine:
    def __init__(self):
        self.rules = []

    def add_rule(self, premises, conclusion):
        self.rules.append((set(premises), conclusion))

    def get_conclusions(self, facts):
        conclusions = set()
        for premises, conclusion in self.rules:
            if premises.issubset(facts):
                conclusions.add(conclusion)
        return conclusions
