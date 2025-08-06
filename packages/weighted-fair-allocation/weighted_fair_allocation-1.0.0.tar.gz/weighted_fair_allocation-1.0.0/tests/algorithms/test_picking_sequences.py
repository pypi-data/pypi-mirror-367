import pytest

from weighted_fair_allocation import model
from weighted_fair_allocation.algorithms.picking_sequences import PickingSequence

def test_picking_sequence_run_simple():
    #arrange
    a = model.Item("a")
    b = model.Item("b")
    c = model.Item("c")
    d = model.Item("d")

    items = set([a,b,c,d])

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:4, b:3, c:2, d:1})

    a1 = model.Agent(1, 1, v1)
    a2 = model.Agent(2, 1, v1)

    instance = model.Instance(set([a1, a2]), items)

    alg = PickingSequence(instance)

    #act
    allocation = alg.run([a1, a2, a1, a2])

    #assert
    assert allocation[model.Agent.unassigned()] == set()
    assert allocation[a1] == set([a,c])
    assert allocation[a2] == set([b,d])

def test_picking_sequence_run_tie_breaking():
    #arrange
    a = model.Item("a")
    b = model.Item("b")
    c = model.Item("c")
    d = model.Item("d")

    items = set([a,b,c,d])

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:1, b:1, c:1, d:1})

    a1 = model.Agent(1, 1, v1)
    a2 = model.Agent(2, 1, v1)

    instance = model.Instance(set([a1, a2]), items)

    alg = PickingSequence(instance)

    #act
    allocation = alg.run([a1, a2, a1, a2])

    #assert
    assert allocation[model.Agent.unassigned()] == set()
    assert allocation[a1] == set([a,c])
    assert allocation[a2] == set([b,d])

@pytest.fixture()
def divisor_sequences_setup():
    #arrange
    a = model.Item("a")
    b = model.Item("b")
    c = model.Item("c")
    d = model.Item("d")
    e = model.Item("e")
    f = model.Item("f")

    items = set([a,b,c,d,e,f])

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:6, b:5, c:4, d:3, e:2, f:1})

    a1 = model.Agent(1, 3, v1, "a_i")
    a2 = model.Agent(2, 2, v1, "a_j")
    a3 = model.Agent(3, 1, v1, "a_k")

    instance = model.Instance(set([a1, a2, a3]), items)
    return ((a,b,c,d,e,f), (a1,a2,a3), instance)


def test_adams_sequence(divisor_sequences_setup):
    #arrange
    items, agents, instance = divisor_sequences_setup
    a,b,c,d,e,f = items
    a1, a2, a3 = agents
    
    alg = PickingSequence(instance)

    #act
    allocation = alg.adams()

    #assert
    assert allocation[model.Agent.unassigned()] == set()
    assert allocation[a1] == set([a,d, f])
    assert allocation[a2] == set([b,e])
    assert allocation[a3] == set([c])

def test_jefferson_sequence(divisor_sequences_setup):
    #arrange
    items, agents, instance = divisor_sequences_setup
    a,b,c,d,e,f = items
    a1, a2, a3 = agents
    
    alg = PickingSequence(instance)

    #act
    allocation = alg.jefferson()

    #assert
    assert allocation[model.Agent.unassigned()] == set()
    assert allocation[a1] == set([a,c,d])
    assert allocation[a2] == set([b,e])
    assert allocation[a3] == set([f])

def test_webster_sequence(divisor_sequences_setup):
    #arrange
    items, agents, instance = divisor_sequences_setup
    a,b,c,d,e,f = items
    a1, a2, a3 = agents
    
    alg = PickingSequence(instance)

    #act
    allocation = alg.webster()

    #assert
    assert allocation[model.Agent.unassigned()] == set()
    assert allocation[a1] == set([a,c,f])
    assert allocation[a2] == set([b,e])
    assert allocation[a3] == set([d])

def test_hill_sequence(divisor_sequences_setup):
    #arrange
    items, agents, instance = divisor_sequences_setup
    a,b,c,d,e,f = items
    a1, a2, a3 = agents
    
    alg = PickingSequence(instance)

    #act
    allocation = alg.hill()

    #assert
    assert allocation[model.Agent.unassigned()] == set()
    assert allocation[a1] == set([a,d,f])
    assert allocation[a2] == set([b,e])
    assert allocation[a3] == set([c])

def test_dean_sequence(divisor_sequences_setup):
    #arrange
    items, agents, instance = divisor_sequences_setup
    a,b,c,d,e,f = items
    a1, a2, a3 = agents
    
    alg = PickingSequence(instance)

    #act
    allocation = alg.dean()

    #assert
    assert allocation[model.Agent.unassigned()] == set()
    assert allocation[a1] == set([a,d,f])
    assert allocation[a2] == set([b,e])
    assert allocation[a3] == set([c])