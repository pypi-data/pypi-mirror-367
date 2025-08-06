import math

from weighted_fair_allocation import model


class NashWelfareAllocation(model.Allocation):
    @classmethod
    def from_allocation(cls, parent: model.Allocation):
        new_instance = cls.__new__(cls)

        new_instance.allocation = parent.allocation.copy()

        return new_instance
    
    @classmethod
    def from_instance(cls, instance:model.Instance):
        return NashWelfareAllocation.from_agents_items(instance.agents, instance.items)
    
    def nash_welfare(self):        
        agents = list(self.allocation.keys())
        agents.remove(model.Agent.unassigned())
        
        return math.prod([self.get_agent_valuation(agent) for agent in agents])
    
    def weighted_nash_welfare(self):
        agents = list(self.allocation.keys())
        agents.remove(model.Agent.unassigned())

        return math.prod([pow(self.get_agent_valuation(agent), agent.weight) for agent in agents])