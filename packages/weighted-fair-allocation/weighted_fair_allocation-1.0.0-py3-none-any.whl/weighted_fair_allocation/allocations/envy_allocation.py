from weighted_fair_allocation import model

from itertools import combinations

from collections import deque

import numpy as np

import graphviz as gv

class EnvyAllocation(model.Allocation):
    @classmethod
    def from_allocation(cls, parent: model.Allocation):
        new_instance = cls.__new__(cls)

        new_instance.allocation = parent.allocation.copy()

        return new_instance
    
    @classmethod
    def from_instance(cls, instance:model.Instance):
        return EnvyAllocation.from_agents_items(instance.agents, instance.items)
    
    def is_WEF(self):
        matrix, _ = self._calculate_envy_matrix()

        return (matrix >= 0).all()
    
    def is_WEF1(self):
        matrix, indexes = self._calculate_envy_matrix()

        agent_lookup = {v: k for k, v in indexes.items()}

        for pair in np.argwhere(matrix < 0):
            a1 = agent_lookup[pair[0]]
            a2 = agent_lookup[pair[1]]

            if not self._are_WEF1(a1, a2):
                return False

        return True
    
    def is_WWEF1(self):
        matrix, indexes = self._calculate_envy_matrix()

        agent_lookup = {v: k for k, v in indexes.items()}

        for pair in np.argwhere(matrix < 0):
            a1 = agent_lookup[pair[0]]
            a2 = agent_lookup[pair[1]]

            if not self._are_WWEF1(a1, a2):
                return False

        return True
    
    def is_WEF_x_y(self, x: float, y: float):
        matrix, indexes = self._calculate_envy_matrix()

        agent_lookup = {v: k for k, v in indexes.items()}

        for pair in np.argwhere(matrix < 0):
            a1 = agent_lookup[pair[0]]
            a2 = agent_lookup[pair[1]]

            if not self._are_WEF_x_y(a1, a2, x, y):
                return False

        return True

    
    def envy_graph(self, name="g", edge_text=True):
        matrix, indexes = self._calculate_envy_matrix()

        dot = gv.Digraph(f"{name}_envy_graph", engine='circo', format='jpg')

        # Build nodes
        agents = list(self.allocation.keys())
        agents.remove(model.Agent.unassigned())
        agents.sort()

        for agent in agents:
            label = str(agent.id) if agent.name == "" else agent.name
            label += f"\n w={agent.weight}" 
            allocated_items = list(self[agent].copy())
            allocated_items.sort(key= lambda i: i.name)
            label += f"\n {allocated_items}" 
            dot.node(f"{name}_{str(agent.id)}", label)

        agent_lookup = {v: k for k, v in indexes.items()}


        # Build invisible cycle to nicely arrange the agents
        for i in range(len(agents) - 1):
            dot.edge(
                f"{name}_{str(agents[i].id)}", 
                f"{name}_{str(agents[i + 1].id)}", 
                style="invis",
                len='1.5'
            )

        dot.edge(
            f"{name}_{str(agents[-1].id)}", 
            f"{name}_{str(agents[0].id)}", 
            style="invis",
            len='1.5'
        )


        # Build actual envy edges
        for pair in np.argwhere(matrix < 0):
            a1 = agent_lookup[pair[0]]
            a2 = agent_lookup[pair[1]]

            
            edge_color = "purple"
            if self._are_WEF_x_y(a1, a2, 1, 1):
                edge_color = "orange"
            if self._are_WWEF1(a1, a2):
                edge_color = "red"
            if self._are_WEF1(a1, a2):
                edge_color = "black"

            if edge_text:
                envy_amount_str = str(abs(matrix[indexes[a1]][indexes[a2]]) / a1.weight)
                if len(envy_amount_str) > 5:
                    envy_amount_str = envy_amount_str[:5]
            else:
                envy_amount_str = ""

            dot.edge(
                f"{name}_{str(a1.id)}", 
                f"{name}_{str(a2.id)}", 
                envy_amount_str, 
                constraint='false',
                color=edge_color,
                len='1.5'
            )

        return dot
    
    def _envy_dict(self):
        envy_dict = dict[model.Agent, set[model.Agent]]()
        agents = list(self.allocation.keys())

        for agent in agents:
            envy_dict[agent] = set[model.Agent]()

        matrix, indexes = self._calculate_envy_matrix()

        agent_lookup = {v: k for k, v in indexes.items()}

        for pair in np.argwhere(matrix < 0):
            a1 = agent_lookup[pair[0]]
            a2 = agent_lookup[pair[1]]

            envy_dict[a1].add(a2)

        return envy_dict
    
    def _envied_by_dict(self):
        envy_dict = dict[model.Agent, set[model.Agent]]()
        agents = list(self.allocation.keys())

        for agent in agents:
            envy_dict[agent] = set[model.Agent]()

        matrix, indexes = self._calculate_envy_matrix()

        agent_lookup = {v: k for k, v in indexes.items()}

        for pair in np.argwhere(matrix < 0):
            a1 = agent_lookup[pair[0]]
            a2 = agent_lookup[pair[1]]

            envy_dict[a2].add(a1)

        return envy_dict

    def _are_WEF1(self, a1: model.Agent, a2: model.Agent):
        for item in self[a2]:
            if (a1.get_valuation(self[a1]) / a1.weight) >= (a1.get_valuation(self[a2].difference(set([item]))) / a2.weight):
               return True
            
        return False
    
    def _get_g_WEF1(self, a1: model.Agent, a2: model.Agent):            
        return [item for item in self[a2] 
                if (a1.get_valuation(self[a1]) / a1.weight) >= (a1.get_valuation(self[a2].difference(set([item]))) / a2.weight)]
    
    def _are_WWEF1(self, a1: model.Agent, a2: model.Agent):
        for item in self[a2]:
            #WEF1 standard case
            if (a1.get_valuation(self[a1]) / a1.weight) >= (a1.get_valuation(self[a2].difference(set([item]))) / a2.weight):
                return True
            
            #copy case
            if (a1.get_valuation(self[a1].union(set([item]))) / a1.weight) >= (a1.get_valuation(self[a2]) / a2.weight):
                return True

        return False
    
    def _get_g_WWEF1(self, a1: model.Agent, a2: model.Agent):
        return [item for item in self[a2] 
                if (a1.get_valuation(self[a1]) / a1.weight) >= (a1.get_valuation(self[a2].difference(set([item]))) / a2.weight)
                or (a1.get_valuation(self[a1].union(set([item]))) / a1.weight) >= (a1.get_valuation(self[a2]) / a2.weight)]

    def _are_WEF_x_y(self, a1: model.Agent, a2: model.Agent, x: float, y: float):
        for item in self[a2]:
            if ((a1.get_valuation(self[a1]) + (y * a1.get_valuation(set([item])))) / a1.weight) >= ((a1.get_valuation(self[a2]) - (x * a1.get_valuation(set([item])))) / a2.weight):
                return True

        return False
    
    def _calculate_envy_matrix(self):
        agents = list(self.allocation.keys())
        agents.remove(model.Agent.unassigned())
        agents.sort()

        indexes = dict[model.Agent, int]()
        for i, agent in enumerate(agents):
            indexes[agent] = i

        matrix = np.zeros((len(agents), len(agents)))

        for a1, a2 in combinations(agents, 2):
            matrix[indexes[a1]][indexes[a2]] = (a1.get_valuation(self[a1]) / a1.weight) - (a1.get_valuation(self[a2]) / a2.weight) 

            matrix[indexes[a2]][indexes[a1]] = (a2.get_valuation(self[a2]) / a2.weight) - (a2.get_valuation(self[a1]) / a1.weight) 

        return matrix, indexes
    
    def has_envy_cycle(self):
        agents = list(self.allocation.keys())
        max_len = len(agents)

        envy_dict = self._envy_dict()

        for agent in agents:
            targets = deque()
            targets.appendleft(agent)

            for i in range(max_len):
                new_targets = list()
                while len(targets) > 0:
                    for target in envy_dict[targets.pop()]:
                        new_targets.append(target)

                if agent in new_targets:
                    return True
                
                for target in new_targets:
                    targets.appendleft(target)
        return False
    
    def _find_envy_cycle(self, agent: model.Agent, ancestors: list[model.Agent], depth:int, envy_dict):
        new_anc = ancestors.copy()
        new_anc.append(agent)

        if depth == 0:
            return None

        new_targets = envy_dict[agent]

        if not new_targets:
            return None

        for target in new_targets:
            if target in new_anc:
                #found cycle
                return new_anc

        
        for target in new_targets:
            if target in new_anc:
                try:
                    start_index = new_anc.index(target)
                    return new_anc[start_index:] + [target]
                except ValueError:
                    # This should not happen if target is in new_anc, but good for robustness
                    return new_anc

        for target in new_targets:
            found_cycle = self._find_envy_cycle(target, new_anc, depth - 1, envy_dict)
            if found_cycle is not None:
                return found_cycle

        return None
        
    def _fix_cycle(self, cycle: list[model.Agent]):
        c = deque(cycle)
        lowest_index_agent = cycle.index(min(cycle, key=lambda a: a.id))
        c.rotate(-lowest_index_agent)
        return list(c)

    def get_envy_cycles(self):
        agents = list(self.allocation.keys())
        agents.sort(key= lambda agent: agent.id)
        max_len = len(agents)

        envy_dict = self._envy_dict()

        cycles = []
        cycles_sets = set()

        agents.remove(model.Agent.unassigned())

        for agent in agents:
            cycle = self._find_envy_cycle(agent, [], max_len, envy_dict)
            if cycle is not None:
                cycle_set = frozenset(cycle)

                if cycle_set not in cycles_sets:
                    cycles.append(self._fix_cycle(cycle))
                    cycles_sets.add(cycle_set)
        
        cycles = sorted(cycles, key=lambda l: len(l))
        return cycles