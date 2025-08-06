from . import exceptions

class Item:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

class Valuation:
    def __init__(self):
        self._val = dict[frozenset[Item], int]()
        self._val[frozenset()] = 0

    def add_valuation(self, items:set[Item], value:int):
        self._val[frozenset(items)] = value

    def get_value(self, items:set[Item]):
        return self._val[frozenset(items)]
    
    def get_preference_order(self):
        order = []

        lookup = dict[int, list[Item]]()
        for k,v in self._val.items():
            if len(k) == 1:
                if not v in lookup:
                    lookup[v] = []
                lookup[v].append(set(k).pop())

        values = sorted(list(lookup.keys()), reverse=True)

        for val in values:
            temp_items = lookup[val].copy()
            order += sorted(temp_items, key=lambda item: item.name)
        return order

class AdditiveValuation(Valuation):
    def _old_add_valuation(self, item: Item, value:int):
        new_dict = {}
        for key in self._val.keys():
            new_dict[key.union(frozenset([item]))] = self._val[key] + value
        
        self._val = self._val | new_dict

    def add_valuation(self, item: Item, value: int):
        return super().add_valuation(set([item]), value)

    def provide_valuations(self, valuation_dict:dict[Item, int]):
        for key in valuation_dict:
            self.add_valuation(key, valuation_dict[key])

    def get_value(self, items):
        return sum([super().get_value(set([item])) for item in items])

class Agent:  
    def __init__(self, id:int, weight:int, valuation:Valuation, name=""):
        self.id = id
        self.weight = weight
        self.valuation = valuation
        self.name = name

    @classmethod
    def unassigned(cls):
        cls.id = 0
        cls.weight = -1
        cls.valuation = Valuation()

        return cls
    
    def __repr__(self):
        if len(self.name) > 0:
            return self.name
        return str(self.id)
    
    def __eq__(self, value):
        if not isinstance(value, Agent):
            raise TypeError(f"{value} is not an agent")
        return self.id == value.id
    
    def __lt__(self, value):
        if not isinstance(value, Agent):
            raise TypeError(f"{value} is not an agent")
        return self.id < value.id
    
    #maybe this breaks stuff later on, good luck future Ties
    def __hash__(self):
        return hash((self.id, self.weight, self.valuation))
    
    def get_valuation(self, items:set[Item]):
        return self.valuation.get_value(items)

class Instance:
    def __init__(self, agents:set[Agent], items:set[Item]):
        self.agents = agents
        self.items = items

    def draw_str(self):
        itemOrder = list(self.items.copy())
        itemOrder.sort(key=lambda item: item.name)

        agents = list(self.agents.copy())
        agents.sort(reverse=True, key=lambda agent: agent.weight)

        agent_cell_length = max(len(agent.name) for agent in agents)
        item_cell_length = max(len(item.name) for item in itemOrder)

        drawing = ""

        header = f"| w | {' '*agent_cell_length} |"
        header2 = f"| - | {'-'*agent_cell_length} |"
        for item in itemOrder:
            padding = item_cell_length - len(item.name)

            header += f" {item.name}{' '*padding} |"
            header2 += f" {'-'*item_cell_length} |"
        header += "\n"
        header2 += "\n"

        drawing += header
        drawing += header2

        for agent in agents:
            name = "agent " + str(agent.id) if agent.name == "" else agent.name
            line = f"| {agent.weight} | {name} |"
            for item in itemOrder:

                val = agent.get_valuation(set([item]))
                padding = item_cell_length - len(str(val))
                line += f" {val}{' '*padding} |"
            
            line += "\n"
            drawing += line

        # print(drawing)
        return drawing

class Allocation:
    def __init__(self,):
        self.allocation = dict[Agent, set[Item]]()

    @classmethod
    def from_agents_items(cls, agents:set[Agent], items:set[Item]):
        alloc = cls()

        alloc.allocation[Agent.unassigned()] = items.copy()
        for agent in agents:
            alloc.allocation[agent] = set()
        return alloc

    @classmethod
    def from_instance(cls, instance:Instance):
        # return Allocation.from_agents_items(instance.agents.copy(), instance.items.copy())
        return Allocation.from_agents_items(instance.agents.copy(), instance.items.copy())
    
    def assign(self, item:Item, agent:Agent):
        for key in self.allocation.keys():
            if item in self.allocation[key]:
                self.allocation[key].remove(item)

        self.allocation[agent].add(item)

    def get_agent_valuation(self, agent:Agent):
        items = self.allocation[agent]
        return agent.get_valuation(items)
    
    def __getitem__(self, agent:Agent):
        return self.allocation[agent]

    def copy(self):
        new_alloc = Allocation()

        for key in self.allocation.keys():
            new_alloc.allocation[key] = set[Item]()
            for item in self.allocation[key]:
                new_alloc.allocation[key].add(item)

        # new_alloc.allocation = self.allocation.copy()

        return new_alloc
    
    def __eq__(self, other):
        if isinstance(other, Allocation):
            agents = self.allocation.keys()
            if set(agents) == set(other.allocation.keys()):
                for agent in agents:
                    if not (self[agent] == other[agent]):
                        return False
                return True
        return False
    
    def __hash__(self):
        temp_d = {}
        for k,v in self.allocation.items():
            temp_d[k] = frozenset(v)

        return hash(frozenset(temp_d.items()))
    
    def __repr__(self):
        temp = self.allocation.copy()
        del temp[Agent.unassigned()]

        return str(temp)