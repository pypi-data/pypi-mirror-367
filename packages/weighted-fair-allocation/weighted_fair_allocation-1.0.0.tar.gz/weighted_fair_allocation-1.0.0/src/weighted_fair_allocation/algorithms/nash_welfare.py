from weighted_fair_allocation import model, utils
from weighted_fair_allocation.allocations.nash_welfare_allocation import NashWelfareAllocation

class MaxNashWelfare():
    def __init__(self, instance:model.Instance):
        self._instance = instance

    def run(self, weighted=False):
        allocs = utils.compute_possible_allocation(self._instance)

        nash_welfare_allocs = [NashWelfareAllocation.from_allocation(alloc) for alloc in allocs]

        if not weighted:
            return max(nash_welfare_allocs, key=lambda alloc: alloc.nash_welfare())
        else:
            return max(nash_welfare_allocs, key=lambda alloc: alloc.weighted_nash_welfare())