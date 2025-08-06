from weighted_fair_allocation import model
from weighted_fair_allocation.algorithms.envy_cycle_elimination import EnvyCycleElimination

def test_envy_cycle_elimination_assigns_all_items():
    #arrange
    a = model.Item("a")
    b = model.Item("b")
    c = model.Item("c")
    d = model.Item("d")

    items = set([a,b,c,d])

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:1, b:2, c:3, d:4})

    a1 = model.Agent(1, 1, v1)
    a2 = model.Agent(2, 1, v1)

    instance = model.Instance(set([a1, a2]), items)

    alg = EnvyCycleElimination(instance)

    #act
    allocation = alg.run([a1, a2], [a,b,c,d])

    #assert
    assert allocation[model.Agent.unassigned()] == set()
    assert allocation[a1] == set([a,c])
    assert allocation[a2] == set([b,d])

def test_envy_cycle_elimination_swap_reallocation():
    #arrange
    a = model.Item('a')
    b = model.Item('b')
    c = model.Item('c')

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:2, b:2, c:1})

    v2 = model.AdditiveValuation()
    v2.provide_valuations({a:1, b:2, c:1})

    v3 = model.AdditiveValuation()
    v3.provide_valuations({a:1, b:1, c:2})

    a1 = model.Agent(1, 1, v1, "i")
    a2 = model.Agent(2, 1, v2, "j")
    a3 = model.Agent(3, 1, v3, "k")

    instance = model.Instance(set([a1, a2, a3]), set([a,b,c]))

    alg = EnvyCycleElimination(instance)

    #act
    allocation = alg.run([a1, a3, a2], [c,b,a])

    #assert
    assert allocation[model.Agent.unassigned()] == set()
    assert allocation[a1] == set([b])
    assert allocation[a2] == set([a])
    assert allocation[a3] == set([c])