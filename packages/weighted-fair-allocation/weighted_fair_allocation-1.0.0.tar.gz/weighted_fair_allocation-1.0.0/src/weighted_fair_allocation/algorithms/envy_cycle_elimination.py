from weighted_fair_allocation import model
from weighted_fair_allocation.allocations.envy_allocation import EnvyAllocation

class EnvyCycleElimination():
    def __init__(self, instance:model.Instance):
        self.instance = instance

    def run(self, agent_order = list[model.Agent](), item_order = list[model.Item]()):
        alloc = EnvyAllocation.from_instance(self.instance)

        a_order = agent_order if agent_order != [] else list(self.instance.agents)
        i_order = item_order if item_order != [] else list(self.instance.items)

        item_index = 0

        while len(alloc[model.Agent.unassigned()]) > 0:
            envied_by = alloc._envied_by_dict()

            agent = next(a for a in a_order if len(envied_by[a]) == 0)

            alloc.assign(i_order[item_index], agent)

            while alloc.has_envy_cycle():
                alloc = self._swap(alloc)

            item_index += 1
                
        return alloc
    
    def _swap(cls, alloc: EnvyAllocation):
        cycle = alloc.get_envy_cycles()[0]

        new_alloc = EnvyAllocation().from_allocation(alloc.copy())

        for index in range(len(cycle) - 1):
            new_alloc.allocation[cycle[index]] = alloc[cycle[index + 1]].copy()
        new_alloc.allocation[cycle[-1]] = alloc[cycle[0]].copy()

        return new_alloc
    
