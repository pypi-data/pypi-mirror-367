import itertools

from weighted_fair_allocation import model

def compute_possible_allocation(instance: model.Instance, empty_bundles=True):
    if empty_bundles:
        splits = _compute_possible_splits(instance.items.copy(), len(instance.agents))
    else:
        splits = _compute_possible_splits_without_empty_bundles(instance.items.copy(), len(instance.agents))

    agent_order = list(instance.agents)

    return [_convert_split_to_alloc(instance, split, agent_order) for split in splits]

def _compute_possible_splits(items: set[model.Item], agents: int):
    allocations = set()

    if agents == 2:
        for i in range(0, len(items) + 1):
            for comb in itertools.combinations(items, i):
                t_items = items.copy()
                s1 = frozenset(comb)
                s2 = frozenset(t_items.difference(comb))
                allocations.add((s1, s2))

    if agents > 2:
        for i in range(0, len(items) + 1):
            for comb in itertools.combinations(items, i):
                t_items = items.copy()
                s1 = frozenset(comb)
                remainder = t_items.difference(comb).copy()
                remainder_allocs = _compute_possible_splits(remainder, agents-1)

                for temp_alloc in remainder_allocs:
                    t = list(temp_alloc)
                    t.insert(0, s1)
                    allocations.add(tuple(t))

    return allocations

def _compute_possible_splits_without_empty_bundles(items: set[model.Item], agents: int):
    allocations = set()

    if agents == 2:
        for i in range(1, len(items)):
            for comb in itertools.combinations(items, i):
                t_items = items.copy()
                s1 = frozenset(comb)
                s2 = frozenset(t_items.difference(comb))
                allocations.add((s1, s2))

    if agents > 2:
        for i in range(1, len(items)):
            for comb in itertools.combinations(items, i):
                t_items = items.copy()
                s1 = frozenset(comb)
                remainder = t_items.difference(comb).copy()
                remainder_allocs = _compute_possible_splits_without_empty_bundles(remainder, agents-1)

                for temp_alloc in remainder_allocs:
                    t = list(temp_alloc)
                    t.insert(0, s1)
                    allocations.add(tuple(t))

    return allocations

def _convert_split_to_alloc(instance: model.Instance, split: tuple[model.Item], agents: list[model.Agent]):
    alloc = model.Allocation().from_instance(instance)

    for items, agent in zip(split, agents):
        for item in items:
            alloc.assign(item, agent)
    
    return alloc

def max_agent(agents:set[model.Agent]):
    max_val = 0
    max_agents = list[model.Agent]()

    for agent in agents:
        if agent.weight > max_val:
            max_val = agent.weight
            max_agents.clear()
        if agent.weight == max_val:
            max_agents.append(agent)

    return sorted(max_agents, key=lambda a: a.name)[0]