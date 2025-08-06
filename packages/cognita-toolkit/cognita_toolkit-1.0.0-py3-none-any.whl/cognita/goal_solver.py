class GoalSolver:
    def __init__(self, factbase, rule_engine):
        self.factbase = factbase
        self.rule_engine = rule_engine

    def solve(self, goal, max_steps=10):
        known = set(self.factbase.get_facts())
        for _ in range(max_steps):
            if goal in known:
                return True
            new_conclusions = self.rule_engine.get_conclusions(known)
            if new_conclusions.issubset(known):
                break
            known.update(new_conclusions)
        return goal in known
