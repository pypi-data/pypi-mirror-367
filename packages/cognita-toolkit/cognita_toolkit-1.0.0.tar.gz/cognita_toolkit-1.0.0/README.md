# Cognita 🧠

**Cognita** is a lightweight symbolic reasoning toolkit for building logic-based intelligent agents.

> 🛠️ Built by [Aditya Kharat](https://pypi.org/user/adityakharat)

### 🔍 What It Does
- Store facts
- Define IF–THEN logic rules
- Solve logical goals using reasoning

### 🚀 Example Use
```python
from cognita.factbase import FactBase
from cognita.rule_engine import RuleEngine
from cognita.goal_solver import GoalSolver

facts = FactBase()
rules = RuleEngine()

facts.add_fact("user(frustrated)")
facts.add_fact("issue(open)")

rules.add_rule(["user(frustrated)", "issue(open)"], "should(escalate)")

goal = "should(escalate)"
solver = GoalSolver(facts, rules)

if solver.solve(goal):
    print("🚨 Escalate!")
else:
    print("😌 No escalation needed.")
```
