import pytest

from weighted_fair_allocation import model

@pytest.fixture
def agent_item_setup():
    i1 = model.Item('1')
    i2 = model.Item('2')

    v1 = model.AdditiveValuation()
    v1.add_valuation(i1, 1)
    v1.add_valuation(i2, 1)

    v2 = model.AdditiveValuation()
    v2.add_valuation(i2, 1)
    v2.add_valuation(i1, 1)

    a1 = model.Agent(1, 1, v1)
    a2 = model.Agent(2, 1, v2)
    return set([a1, a2]), set([i1, i2])


def test_AgentCreation():
    agent = model.Agent(1, 1, model.Valuation())

    assert agent.id == 1
    assert agent.weight == 1

def test_EmptyAgentCreation():
    agent = model.Agent.unassigned()
    
    assert agent.id == 0
    assert agent.weight == -1

def test_ItemCreation():
    item = model.Item("candy")

    assert item.name == "candy"

def test_Agent_get_valuation():
    v = model.AdditiveValuation()
    
    a = model.Item('a')

    v.add_valuation(a, 2)

    agent = model.Agent(1, 1, v)

    assert agent.get_valuation(set([a])) == 2

def test_FAInstance_creation(agent_item_setup):
    #arrange
    agents, items = agent_item_setup

    #act
    instance = model.Instance(agents, items)

    #assert
    assert instance.agents == agents
    assert instance.items == items

def test_allocation_creation(agent_item_setup):
    #arrange
    agents, items = agent_item_setup

    #act
    a = model.Allocation.from_agents_items(agents, items)

    #assert
    a1 = agents.pop()
    a2 = agents.pop()

    assert a.allocation[model.Agent.unassigned()] == items
    assert a.allocation[a1] == set()
    assert a.allocation[a2] == set()

def test_allocation_creation_instance(agent_item_setup):
    #arrange
    agents, items = agent_item_setup

    instance = model.Instance(agents, items)

    #act
    a = model.Allocation.from_instance(instance)

    #assert
    a1 = agents.pop()
    a2 = agents.pop()

    assert a.allocation[model.Agent.unassigned()] == items
    assert a.allocation[a1] == set()
    assert a.allocation[a2] == set()

def test_allocation_assignment(agent_item_setup):
    #arrange
    agents, items = agent_item_setup

    instance = model.Instance(agents, items)

    a = model.Allocation.from_instance(instance)
    
    #act
    a1 = agents.pop()
    i1 = items.pop()

    a.assign(i1, a1)

    #assert
    assert a.allocation[model.Agent.unassigned()] == items
    assert a.allocation[a1] == set([i1])

def test_allocation_mapping_overload(agent_item_setup):
    #arrange
    agents, items = agent_item_setup

    instance = model.Instance(agents, items)

    a = model.Allocation.from_instance(instance)
    
    #act
    a1 = agents.pop()
    i1 = items.pop()

    a.assign(i1, a1)

    #assert
    assert a[model.Agent.unassigned()] == items
    assert a[a1] == set([i1])

def test_allocation_agent_valuation(agent_item_setup):
    #arrange
    agents, items = agent_item_setup

    instance = model.Instance(agents, items)

    a = model.Allocation.from_instance(instance)

    a1 = agents.pop()
    i1 = items.pop()

    a.assign(i1, a1)

    #act
    val = a.get_agent_valuation(a1)

    #assert
    assert val == 1

def test_allocation_equivalence():
    #arrange
    a = model.Item('a')
    b = model.Item('b')
    c = model.Item('c')
    d = model.Item('d')

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:1, b:1, c:1, d:1})

    a1 = model.Agent(1, 1, v1, "a_1")
    a2 = model.Agent(2, 1, v1, "a_2")

    alloc1 = model.Allocation().from_agents_items(set([a1, a2]), set([a,b,c,d]))
    alloc2 = model.Allocation().from_agents_items(set([a1, a2]), set([a,b,c,d]))

    alloc1.assign(a, a1)
    alloc1.assign(b, a1)
    alloc1.assign(c, a2)
    alloc1.assign(d, a2)

    alloc2.assign(a, a1)
    alloc2.assign(b, a1)
    alloc2.assign(c, a2)

    #assert
    assert not (alloc1 == alloc2)

    alloc2.assign(d, a2)

    assert (alloc1 == alloc2)



