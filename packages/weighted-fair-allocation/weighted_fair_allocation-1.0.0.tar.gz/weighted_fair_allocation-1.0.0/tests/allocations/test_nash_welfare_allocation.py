from weighted_fair_allocation import model
from weighted_fair_allocation.allocations.nash_welfare_allocation import NashWelfareAllocation

def test_welfare_simple_1():
    #arrange
    a = model.Item('a')
    b = model.Item('b')

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:2, b:1})

    v2 = model.AdditiveValuation()
    v2.provide_valuations({a:1, b:2})

    a1 = model.Agent(1, 1, v1)
    a2 = model.Agent(2, 1, v2)

    alloc = NashWelfareAllocation.from_agents_items(set([a1, a2]), set([a,b]))
    alloc.assign(b, a1)
    alloc.assign(a, a2)

    #act
    val = alloc.nash_welfare()

    #assert
    assert val == 1

def test_welfare_simple_2():
    #arrange
    a = model.Item('a')
    b = model.Item('b')

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:2, b:1})

    v2 = model.AdditiveValuation()
    v2.provide_valuations({a:1, b:2})

    a1 = model.Agent(1, 1, v1)
    a2 = model.Agent(2, 1, v2)

    alloc = NashWelfareAllocation.from_agents_items(set([a1, a2]), set([a,b]))
    alloc.assign(a, a1)
    alloc.assign(b, a2)

    #act
    val = alloc.nash_welfare()

    #assert
    assert val == 4

def test_welfare_simple_3():
    #arrange
    a = model.Item('a')
    b = model.Item('b')

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:2, b:1})

    v2 = model.AdditiveValuation()
    v2.provide_valuations({a:2, b:2})

    a1 = model.Agent(1, 1, v1)
    a2 = model.Agent(2, 1, v2)

    alloc = NashWelfareAllocation.from_agents_items(set([a1, a2]), set([a,b]))
    alloc.assign(b, a1)
    alloc.assign(a, a2)

    #act
    val = alloc.nash_welfare()

    #assert
    assert val == 2

def test_weighted_welfare_1():
    #arrange
    a = model.Item('a')
    b = model.Item('b')

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:2, b:1})

    v2 = model.AdditiveValuation()
    v2.provide_valuations({a:2, b:1})

    a1 = model.Agent(1, 2, v1)
    a2 = model.Agent(2, 1, v2)

    alloc = NashWelfareAllocation.from_agents_items(set([a1, a2]), set([a,b]))
    alloc.assign(a, a1)
    alloc.assign(b, a2)

    #act
    val = alloc.weighted_nash_welfare()

    #assert
    assert val == 4

def test_weighted_welfare_2():
    #arrange
    a = model.Item('a')
    b = model.Item('b')

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:2, b:1})

    v2 = model.AdditiveValuation()
    v2.provide_valuations({a:2, b:2})

    a1 = model.Agent(1, 3, v1)
    a2 = model.Agent(2, 2, v2)

    alloc = NashWelfareAllocation.from_agents_items(set([a1, a2]), set([a,b]))
    alloc.assign(a, a1)
    alloc.assign(b, a2)

    #act
    val = alloc.weighted_nash_welfare()

    #assert
    assert val == 32