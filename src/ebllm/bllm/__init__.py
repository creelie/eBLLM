"""BLLM: language models and other proposers inside a loop of checks with a guaranteed bound.

    schedules    the entropy law and its relatives: how many runs of each check, at least cost
    checks       exact and weak checks (expansion, interpolation, random evaluation, the Lean kernel)
    agents       six subagents, one for each move by which hard proofs are found, and Lean tactics
    coordinator  the loop: agents propose, cascades check, memory keeps, the budget is split by law
    vault        long-term memory written as an Obsidian vault
    proposers    connectors to hosted and local language models (the user's own keys)
    gap          the gap law between human and LLM ideas, on the data of arXiv:2607.01233
    neuro        a spiking selector that learns which agent to run, and real connectomes
    tasks        stepwise records of solved and open problems, with the plan on each open step
"""
from .coordinator import Coordinator
from .agents import DEMO_PROBLEMS, LEAN_PROBLEMS, Problem, default_agents
from .gap import idea_gap_table, optimal_cost, optimal_profile, search_cost
from .neuro import Connectome, SpikingSelector
from .tasks import load_tasks

__all__ = ["Coordinator", "DEMO_PROBLEMS", "LEAN_PROBLEMS", "Problem", "default_agents",
           "idea_gap_table", "optimal_cost", "optimal_profile", "search_cost",
           "Connectome", "SpikingSelector", "load_tasks"]
