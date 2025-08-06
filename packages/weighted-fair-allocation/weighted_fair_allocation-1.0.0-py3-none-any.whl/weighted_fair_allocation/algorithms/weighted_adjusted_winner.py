from weighted_fair_allocation import model, exceptions

class WeightedAdjustedWinner():
    def __init__(self, instance:model.Instance):
        if len(instance.agents) != 2:
            raise exceptions.InstanceError("Adjusted winner procedure only works for 2 agents.")
        self._instance = instance

        self._alloc = model.Allocation.from_instance(self._instance)

        temp_agents = instance.agents.copy()

        a1 = temp_agents.pop()
        a2 = temp_agents.pop()

        if a1.weight >= a2.weight:
            self._a_i = a1
            self._a_j = a2
        else:
            self._a_i = a2
            self._a_j = a1

    def run(self):

        itemOrder = self._calculate_item_order()

        d = 1
        
        while (1/self._a_i.weight) * self._a_i.get_valuation(set(itemOrder[:d])) < (1/self._a_j.weight) * self._a_i.get_valuation(set(itemOrder[d+1:])):
            d += 1
        
        for item in itemOrder[:d]:
            self._alloc.assign(item, self._a_i)

        for item in itemOrder[d:]:
            self._alloc.assign(item, self._a_j)

        return self._alloc
    
    
    def _calculate_item_order(self):
        item_dict = dict[float, list[model.Item]]()

        for item in self._instance.items:
            val = self._a_i.get_valuation(set([item])) / self._a_j.get_valuation(set([item]))

            if val not in item_dict:
                item_dict[val] = []
            item_dict[val].append(item)

        item_order = list[model.Item]()
        for key in sorted(item_dict.keys(), reverse=True):
            temp_items = sorted(item_dict[key], reverse=True, key=lambda item: self._a_i.get_valuation(set([item])))
            item_order.extend(temp_items)

        return item_order
    
    def _alt_calculate_item_order(self):
        item_dict = dict[float, list[model.Item]]()

        for item in self._instance.items:
            val = self._a_i.get_valuation(set([item])) / self._a_j.get_valuation(set([item]))

            if val not in item_dict:
                item_dict[val] = []
            item_dict[val].append(item)

        item_order = list[model.Item]()
        for key in sorted(item_dict.keys(), reverse=True):
            temp_items = sorted(item_dict[key], key=lambda item: item.name)
            item_order.extend(temp_items)

        return item_order
    
    def _run_visualization(self, itemOrder):

        d = 1
        
        while (1/self._a_i.weight) * self._a_i.get_valuation(set(itemOrder[:d])) < (1/self._a_j.weight) * self._a_i.get_valuation(set(itemOrder[d+1:])):
            d += 1
        
        for item in itemOrder[:d]:
            self._alloc.assign(item, self._a_i)

        for item in itemOrder[d:]:
            self._alloc.assign(item, self._a_j)

        return self._alloc, d