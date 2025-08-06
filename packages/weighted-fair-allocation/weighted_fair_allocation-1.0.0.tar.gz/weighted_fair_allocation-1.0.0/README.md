# Weighted Fair Allocation

An implementation of the weighted setting for the [fair allocation problem](https://en.wikipedia.org/wiki/Fair_item_allocation) (see [weighted fair allocation problem](https://www.sciencedirect.com/science/article/pii/S0020019024000498)), with implementations of common allocation algorithms. Created as experimental tooling for research purposes.

## Installation

Using a python>=3.11 environment, the package can be installed using
``pip install weighted-fair-allocation``

## Basic usage
Creation of a problem instance:
```py
import weighted_fair_allocation.model as wfa

# Specify the set of items
a = wfa.Item('a')
b = wfa.Item('b')
c = wfa.Item('c')
items = set([a, b, c])

# Create valuations for 2 agents
valuation_1 = wfa.AdditiveValuation()
valuation_1.provide_valuations({a:1, b:2, c:3})

valuation_2 = wfa.AdditiveValuation()
valuation_2.provide_valuations({a:3, b:2, c:1})

# Create the set of agents
agent_i = wfa.Agent(
    1,              # Id 
    4,              # Weight
    valuation_1,    # Used valuation
    "i"             # Label
)
agent_j = wfa.Agent(2, 1, valuation_2, "j")
agents = set([agent_i, agent_j])

# Create the problem instance
instance = wfa.Instance(agents, items)

# Print a table view of the instance
print(instance.draw_str())
#   | w |   | a | b | c |                                                    
#   | - | - | - | - | - |
#   | 4 | i | 1 | 2 | 3 |
#   | 1 | j | 3 | 2 | 1 |
```

Now using this problem instance we can manually create an allocation:

```python
# Create an allocation
allocation = wfa.Allocation().from_instance(instance)

# Assign the items to an agent
allocation.assign(a, agent_i)
allocation.assign(b, agent_i)
allocation.assign(c, agent_j)

print(allocation)
# {j: {c}, i: {a, b}}
```

Or use one of the common algorithms to calculate an allocation:
### Weighted adjusted winner procedure
Only defined for instances with 2 agents, results in WEF1 + PO [[Chakraborty et al. 2019](https://arxiv.org/abs/1909.10502)] (+ acyclic) allocations.

```python
from weighted_fair_allocation.algorithms.weighted_adjusted_winner import WeightedAdjustedWinner

# Create an instance of the algorithm and run it
alloc = WeightedAdjustedWinner(instance).run()
print(alloc)
# {j: {a}, i: {b, c}}
```

### Picking sequences
Manually specify a picking sequence:

```python
from weighted_fair_allocation.algorithms.picking_sequences import PickingSequence

# Create an picking sequence instance
alg = PickingSequence(instance)

# Specify a sequence over the agents of length (len(items))
sequence = [agent_i, agent_j, agent_i]

# Run the picking sequence using the specified sequence
alloc = alg.run(sequence)
print(alloc)
# {i: {b, c}, j: {a}}
```

Or use one of the divisor methods, all of which result in WWEF1 allocations (additionally Adams is WEF1 and Jefferson is WPROP1)[[Chakraborty et al. 2021](https://arxiv.org/abs/2104.14347)].

```python
alloc = alg.adams()
alloc = alg.jefferson()
alloc = alg.webster()
alloc = alg.hill()
alloc = alg.dean()
```

Or generate the picking sequences which are guaranteed to result in allocations with a fairness guarantee:
- WEF1 [[Chakraborty et al. 2021](https://arxiv.org/abs/2104.14347)]
- WWEF1 [[Chakraborty et al. 2021](https://arxiv.org/abs/2104.14347)]
- WEF $(x, 1-x)$ (or parameterized WEF) [[Chakraborty et al. 2021](https://arxiv.org/abs/2112.04166)]
- best-of-both worlds (bobw) fairness [[Aziz et al. 2023](https://www.cs.toronto.edu/~emicha/papers/wbobw.pdf)]

```python
sequences = alg.get_valid_sequences_WEF1()
sequences = alg.get_valid_sequences_WWEF1()
sequences = alg.get_valid_sequences_param_WEF()
sequences = alg.get_valid_sequences_bobw()
```

### Max Nash welfare
EF1 + PO allocations [[Caragiannis et al. 2019](https://dl.acm.org/doi/10.1145/3355902)]
```python
from weighted_fair_allocation.algorithms.nash_welfare import MaxNashWelfare

alloc = MaxNashWelfare(instance).run()
print(alloc)
# {j: {a, b}, i: {c}}
```

### Max weighted Nash welfare
WWEF1 + PO allocations [[Chakraborty et al. 2019](https://arxiv.org/abs/1909.10502)]
```python
from weighted_fair_allocation.algorithms.nash_welfare import MaxNashWelfare

alloc = MaxNashWelfare(instance).run(weighted=True)
print(alloc)
# {j: {a}, i: {b, c}}
```