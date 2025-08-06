from weighted_fair_allocation import model
from weighted_fair_allocation.exceptions import SequenceError
from itertools import permutations

import math

from decimal import *

class PickingSequence():
    def __init__(self, instance: model.Instance):
        self._instance = instance
        self.agents = instance.agents.copy()
        self.items = instance.items.copy()

        self.preference_order = dict[model.Agent, list[model.Item]]()
        for agent in self.agents:

            #Special sorting needed as we want items to be ordered in reverse on value and tiebreaks in lexicographical order (not reverse)
            temp_dict = dict[int, list[model.Item]]()
            for item in self.items.copy():
                item_val = agent.get_valuation(set([item]))
                if item_val not in temp_dict:
                    temp_dict[item_val] = []
                temp_dict[item_val].append(item)

            pref = []
            for val in sorted(list(temp_dict.keys()), reverse=True):
                temp_items = temp_dict[val]
                temp_items.sort(key=lambda i: i.name)
                pref.extend(temp_items)

            self.preference_order[agent] = pref

    def run(self, sequence: list[model.Agent]):
        alloc = model.Allocation().from_agents_items(self.agents, self.items)
        
        if len(sequence) != len(self.items):
            raise SequenceError("Sequence not the same size as the number of items to be allocated")

        temp_items = self.items.copy()

        for agent in sequence:
            selected_item = next(item for item in self.preference_order[agent] if item in self.items)
            self.items.remove(selected_item)
            alloc.assign(selected_item, agent)

        self.items = temp_items

        return alloc
    
    def adams(self, tie_breaking_lower_weighted=False) -> model.Allocation:
        """t / w_i"""

        sequence = self._divisor_method(lambda t: t, tie_breaking_lower_weighted=tie_breaking_lower_weighted)

        return self.run(sequence)

    def jefferson(self) -> model.Allocation:
        """t+1 / w_i"""

        sequence = self._divisor_method(lambda t: t+1)
        
        return self.run(sequence)

    def webster(self) -> model.Allocation:
        """t + (1/2) / w-i"""

        sequence = self._divisor_method(lambda t: t+(1/2))
        
        return self.run(sequence)

    def hill(self) -> model.Allocation:
        """sqrt(t(t+1)) / w_i"""
        
        sequence = self._divisor_method(lambda t: math.sqrt(t * (t+1)))
        
        return self.run(sequence)

    def dean(self) -> model.Allocation:
        """(t(t+1) / t + (1/2)) / w_i"""
        
        sequence = self._divisor_method(lambda t: ((t * (t+1)) / (t + (1/2))))
        
        return self.run(sequence)
    
    def wef_x_y(self, x) -> model.Allocation:
        """t_i + (1-x) / w_i"""

        sequence = self._divisor_method(lambda t: (t + (1 - x)))

        return self.run(sequence)

    def _divisor_method(self, div_func, tie_breaking_lower_weighted=False) -> list[model.Agent]:
        seq = []

        while len(seq) < len(self.items):
            div_values_min = -1
            div_values_agents = []

            for agent in self.agents:
                div_val = div_func(seq.count(agent)) / agent.weight
                if div_values_min == -1:
                    div_values_min = div_val

                if div_val == div_values_min:
                    div_values_agents.append(agent)
                if div_val < div_values_min:
                    div_values_agents = [agent]
                    div_values_min = div_val
                

            assert len(div_values_agents) > 0

            if tie_breaking_lower_weighted:
                div_values_agents.sort(key=lambda agent: agent.weight)
            else:
                div_values_agents.sort(key=lambda agent: agent.weight, reverse=True)

            seq.append(div_values_agents[0])

        return seq
    
    def _WEF1_valid_sequence(self, seq: list[model.Agent]) -> bool:
        for (a1, a2) in permutations(self.agents, 2):

            t_a1 = seq.count(a1)
            t_a2 = seq.count(a2)

            if (t_a2 > 1) and (t_a1 / (t_a2 - 1) < a1.weight / a2.weight):
                    return False
        
        return True
    
    
    def _param_WEF_valid_sequence(self, seq: list[model.Agent], x: float):
        for (a1, a2) in permutations(self.agents, 2):

            t_a1 = seq.count(a1)
            t_a2 = seq.count(a2)

            if (t_a1 + (1 - x) < (a1.weight / a2.weight) * (t_a2 - x)):
                    return False
        
        return True
    
    def _WWEF1_valid_sequence(self, seq: list[model.Agent]) -> bool:
        for (a1, a2) in permutations(self.agents, 2):
            t_a1 = seq.count(a1)
            t_a2 = seq.count(a2)
            if (t_a2 > 1):
                if (a1.weight >= a2.weight) and (t_a1 / (t_a2 - 1)) < (a1.weight / a2.weight):
                    return False
                    
                if (a1.weight <= a2.weight) and ((t_a1 + 1) / t_a2) < (a1.weight / a2.weight):
                    return False
        return True
    
    def _bobw_valid_sequence(self, seq: list[model.Agent]) -> bool:
        total_weight = sum([a.weight for a in self.agents])

        a_i = seq[-1]

        new_seq = seq[:-1]

        other_agents = self.agents.copy().difference(set([a_i]))
        for a_j in other_agents:
            t_i = new_seq.count(a_i)
            t_j = new_seq.count(a_j)

            if (t_i > 0) and (t_j == 0):
                return False
            
            val = math.floor(((t_i * (a_j.weight / total_weight)) / (a_i.weight / total_weight)))
            if (t_i > 0) and (t_j > 0) and (t_j < math.floor(Decimal((t_i * (a_j.weight / total_weight)) / (a_i.weight / total_weight)))):
                return False
        
        return True
    
    def _get_extreme_bobw_sequence(self) -> list[model.Agent]:
        agent_order = sorted(self.agents.copy(), key=lambda agent: agent.weight)

        seq = list[model.Agent]()

        while len(seq) < len(self.items):
            for agent in agent_order:
                new_seq = seq.copy()
                new_seq.append(agent)
                if self._bobw_valid_sequence(new_seq):
                    seq = new_seq
                    break
                
        return seq

    def _get_valid_sequence_property(self, property) -> list[list[model.Agent]]:
        sequences = [[]]

        new_sequences = []

        agent_order = sorted(self.agents.copy(), key=lambda agent: agent.weight, reverse=True)

        for item in self.items:
            for seq in sequences:
                for a in agent_order:
                    new_seq = seq.copy()
                    new_seq.append(a)

                    if property(new_seq):
                        new_sequences.append(new_seq)
                
            sequences = new_sequences.copy()
            new_sequences.clear()

        return sequences
        

    def get_valid_sequences_WEF1(self) -> list[list[model.Agent]]:
        return self._get_valid_sequence_property(self._WEF1_valid_sequence)
    
    def get_valid_sequences_WWEF1(self) -> list[list[model.Agent]]:
        return self._get_valid_sequence_property(self._WWEF1_valid_sequence)
    
    def get_valid_sequences_bobw(self) -> list[list[model.Agent]]:
        return self._get_valid_sequence_property(self._bobw_valid_sequence)
    
    def check_valid_sequence_param_WEF(self, x) -> list[list[model.Agent]]:
        sequences = [[]]

        new_sequences = []

        for item in self.items:
            for seq in sequences:
                for a in self.agents:
                    new_seq = seq.copy()
                    new_seq.append(a)

                    if self._param_WEF_valid_sequence(new_seq, x):
                        new_sequences.append(new_seq)
                
            sequences = new_sequences.copy()
            new_sequences.clear()

        return sequences
    
    def get_valid_sequences_param_WEF(self) -> list[list[model.Agent]]:
        sequences = set[tuple]()

        for val in range(101):
            x = val/100
            for seq in self.check_valid_sequence_param_WEF(x):
                if tuple(seq) not in sequences:
                    sequences.add(tuple(seq))

        valids = [list(seq) for seq in sequences]

        return valids
