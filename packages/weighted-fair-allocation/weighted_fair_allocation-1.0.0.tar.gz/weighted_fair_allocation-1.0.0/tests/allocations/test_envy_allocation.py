import pytest

import random

from weighted_fair_allocation import model
from weighted_fair_allocation.allocations import envy_allocation


def build_random_valuation(items:set[model.Item]):
    v = model.AdditiveValuation()

    for item in items:
        v.add_valuation(item, random.randint(1,10))

    return v

@pytest.fixture
def build_equal_weighted_instance_2_agents():
    a = model.Item('a')
    b = model.Item('b')
    c = model.Item('c')
    d = model.Item('d')

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:1, b:2, c:3, d:4})

    v2 = model.AdditiveValuation()
    v2.provide_valuations({a:4, b:3, c:2, d:1})

    a1 = model.Agent(1, 1, v1)
    a2 = model.Agent(2, 1, v2)

    return model.Instance(set([a1, a2]), set([a,b,c,d]))

def test_calculate_unweighted_envy():
    #arrange
    a = model.Item('a')
    b = model.Item('b')
    c = model.Item('c')
    d = model.Item('d')

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:1, b:2, c:3, d:4})

    v2 = model.AdditiveValuation()
    v2.provide_valuations({a:4, b:3, c:2, d:1})

    a1 = model.Agent(1, 1, v1)
    a2 = model.Agent(2, 1, v2)

    allocation = envy_allocation.EnvyAllocation.from_agents_items(set([a1, a2]), set([a,b,c,d]))

    #act
    allocation.assign(a, a1)
    allocation.assign(b, a1)
    allocation.assign(c, a2)
    allocation.assign(d, a2)

    matrix, indexer = allocation._calculate_envy_matrix()

    #assert
    assert matrix[indexer[a1]][indexer[a1]] == 0
    assert matrix[indexer[a2]][indexer[a2]] == 0

    assert matrix[indexer[a1]][indexer[a2]] == -4
    assert matrix[indexer[a2]][indexer[a1]] == -4

def test_calculate_weighted_envy():
    #arrange
    a = model.Item('a')
    b = model.Item('b')
    c = model.Item('c')
    d = model.Item('d')

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:1, b:2, c:3, d:4})

    v2 = model.AdditiveValuation()
    v2.provide_valuations({a:4, b:3, c:2, d:1})

    a1 = model.Agent(1, 2, v1)
    a2 = model.Agent(2, 1, v2)

    allocation = envy_allocation.EnvyAllocation.from_agents_items(set([a1, a2]), set([a,b,c,d]))

    #act
    allocation.assign(a, a1)
    allocation.assign(b, a1)
    allocation.assign(c, a2)
    allocation.assign(d, a2)

    matrix, indexer = allocation._calculate_envy_matrix()

    #assert
    assert matrix[indexer[a1]][indexer[a1]] == 0
    assert matrix[indexer[a2]][indexer[a2]] == 0

    assert matrix[indexer[a1]][indexer[a2]] == -5.5
    assert matrix[indexer[a2]][indexer[a1]] == -0.5

def test_is_WEF():
    #arrange
    a = model.Item('a')
    b = model.Item('b')
    c = model.Item('c')
    d = model.Item('d')

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:1, b:2, c:3, d:4})

    v2 = model.AdditiveValuation()
    v2.provide_valuations({a:4, b:3, c:2, d:1})

    a1 = model.Agent(1, 1, v1)
    a2 = model.Agent(2, 1, v2)

    not_WEF = envy_allocation.EnvyAllocation.from_agents_items(set([a1, a2]), set([a,b,c,d]))

    not_WEF.assign(a, a1)
    not_WEF.assign(b, a1)
    not_WEF.assign(c, a2)
    not_WEF.assign(d, a2)

    WEF = envy_allocation.EnvyAllocation.from_agents_items(set([a1, a2]), set([a,b,c,d]))

    WEF.assign(a, a2)
    WEF.assign(b, a2)
    WEF.assign(c, a1)
    WEF.assign(d, a1)

    #assert
    assert not_WEF.is_WEF() == False
    assert WEF.is_WEF() == True

def test_is_WEF1():
    #arrange
    a = model.Item('a')
    b = model.Item('b')
    c = model.Item('c')
    d = model.Item('d')
    e = model.Item('e')

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:2, b:2, c:1, d:2, e:3})

    v2 = model.AdditiveValuation()
    v2.provide_valuations({a:1, b:1, c:1, d:2, e:1})

    v3 = model.AdditiveValuation()
    v3.provide_valuations({a:1, b:1, c:2, d:2, e:2})

    a1 = model.Agent(1, 2, v1)
    a2 = model.Agent(2, 1, v2)
    a3 = model.Agent(3, 1, v3)

    WEF1 = envy_allocation.EnvyAllocation.from_agents_items(set([a1, a2, a3]), set([a,b,c,d,e]))

    WEF1.assign(a, a1)
    WEF1.assign(b, a1)
    WEF1.assign(c, a2)
    WEF1.assign(d, a2)
    WEF1.assign(e, a3)

    not_WEF1 = envy_allocation.EnvyAllocation.from_agents_items(set([a1, a2, a3]), set([a,b,c,d,e]))

    not_WEF1.assign(a, a1)
    not_WEF1.assign(b, a2)
    not_WEF1.assign(c, a2)
    not_WEF1.assign(d, a2)
    not_WEF1.assign(e, a3)

    #assert
    assert WEF1.is_WEF() == False
    assert WEF1.is_WEF1() == True

    assert not_WEF1.is_WEF() == False
    assert not_WEF1.is_WEF1() == False

def test_anon_envy_dict():
    #arrange
    a = model.Item('a')
    b = model.Item('b')
    c = model.Item('c')
    d = model.Item('d')
    e = model.Item('e')

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:2, b:2, c:1, d:2, e:3})

    v2 = model.AdditiveValuation()
    v2.provide_valuations({a:1, b:1, c:1, d:2, e:1})

    v3 = model.AdditiveValuation()
    v3.provide_valuations({a:1, b:1, c:2, d:2, e:2})

    a1 = model.Agent(1, 2, v1)
    a2 = model.Agent(2, 1, v2)
    a3 = model.Agent(3, 1, v3)

    WEF1 = envy_allocation.EnvyAllocation.from_agents_items(set([a1, a2, a3]), set([a,b,c,d,e]))

    WEF1.assign(a, a1)
    WEF1.assign(b, a1)
    WEF1.assign(c, a2)
    WEF1.assign(d, a2)
    WEF1.assign(e, a3)

    #act
    envy_dict = WEF1._envy_dict()

    #assert
    assert envy_dict[a1] == set([a2, a3])
    assert envy_dict[a2] == set()
    assert envy_dict[a3] == set([a2])


def test_anon_are_WEF1():
    #arrange
    a = model.Item('a')
    b = model.Item('b')
    c = model.Item('c')

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:3, b:2, c:3})

    v2 = model.AdditiveValuation()
    v2.provide_valuations({a:1, b:2, c:1})

    v3 = model.AdditiveValuation()
    v3.provide_valuations({a:1, b:2, c:3})

    a1 = model.Agent(1, 2, v1)
    a2 = model.Agent(2, 1, v2)
    a3 = model.Agent(3, 2, v3)

    not_WEF1 = envy_allocation.EnvyAllocation.from_agents_items(set([a1, a2]), set([a,b,c]))
    
    not_WEF1.assign(a, a2)
    not_WEF1.assign(b, a2)
    not_WEF1.assign(c, a1)

    WEF1 = envy_allocation.EnvyAllocation.from_agents_items(set([a3, a2]), set([a,b,c]))

    WEF1.assign(a, a2)
    WEF1.assign(b, a2)
    WEF1.assign(c, a3)

    #assert
    assert not_WEF1._are_WEF1(a1, a2) == False
    assert not_WEF1._are_WEF1(a2, a1) == True

    assert WEF1._are_WEF1(a3, a2) == True
    assert WEF1._are_WEF1(a2, a3) == True

def test_anon_are_WWEF1():
    #arrange
    a = model.Item('a')
    b = model.Item('b')
    c = model.Item('c')

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:1, b:1, c:1})

    v2 = model.AdditiveValuation()
    v2.provide_valuations({a:3, b:3, c:1})

    a1 = model.Agent(1, 2, v1)
    a2 = model.Agent(2, 1, v2)

    alloc = envy_allocation.EnvyAllocation.from_agents_items(set([a1, a2]), set([a,b,c]))

    alloc.assign(a, a1)
    alloc.assign(b, a1)
    alloc.assign(c, a2)

    #assert
    assert alloc._are_WEF1(a1, a2) == True
    assert alloc._are_WEF1(a2, a1) == False

    assert alloc._are_WWEF1(a1, a2) == True
    assert alloc._are_WWEF1(a2, a1) == True

def test_anon_are_WEF_x_y():
    #arrange
    a = model.Item('a')
    b = model.Item('b')
    c = model.Item('c')

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:4, b:3, c:3})

    v2 = model.AdditiveValuation()
    v2.provide_valuations({a:1, b:1, c:1})

    a1 = model.Agent(1, 2, v1)
    a2 = model.Agent(2, 1, v2)

    alloc = envy_allocation.EnvyAllocation.from_agents_items(set([a1, a2]), set([a,b,c]))

    alloc.assign(a, a1)
    alloc.assign(b, a2)
    alloc.assign(c, a2)

    #assert
    assert alloc.is_WEF() == False

    assert alloc._are_WEF1(a1, a2) == False
    assert alloc._are_WWEF1(a1, a2) == False

    assert alloc._are_WEF_x_y(a1, a2, 1, 1) == True
    assert alloc._are_WEF_x_y(a1, a2, 3/2, 0) == True
    assert alloc._are_WEF_x_y(a1, a2, 0, 3/2) == False
    assert alloc._are_WEF_x_y(a1, a2, 0, 2) == False


def test_has_envy_cycle():
    #arrange
    a = model.Item('a')
    b = model.Item('b')

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:2, b:1})

    v2 = model.AdditiveValuation()
    v2.provide_valuations({a:1, b:2})

    a1 = model.Agent(1, 1, v1)
    a2 = model.Agent(2, 1, v2)

    alloc = envy_allocation.EnvyAllocation.from_agents_items(set([a1, a2]), set([a,b]))

    alloc.assign(b, a1)
    alloc.assign(a, a2)

    #act & assert
    assert alloc.has_envy_cycle() == True


def test_find_envy_cycle_simple():
    #arrange
    a = model.Item('a')
    b = model.Item('b')

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:2, b:1})

    v2 = model.AdditiveValuation()
    v2.provide_valuations({a:1, b:2})

    a1 = model.Agent(1, 1, v1)
    a2 = model.Agent(2, 1, v2)

    alloc = envy_allocation.EnvyAllocation.from_agents_items(set([a1, a2]), set([a,b]))

    alloc.assign(b, a1)
    alloc.assign(a, a2)

    envy_dict = alloc._envy_dict()

    #act
    cycle = alloc._find_envy_cycle(a1, [], 2, envy_dict)

    #assert
    assert cycle == [a1, a2]

def test_find_envy_cycle_3_agents():
    #arrange
    a = model.Item('a')
    b = model.Item('b')
    c = model.Item('c')

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:2, b:1, c:1})

    v2 = model.AdditiveValuation()
    v2.provide_valuations({a:1, b:2, c:1})

    v3 = model.AdditiveValuation()
    v3.provide_valuations({a:1, b:1, c:2})

    a1 = model.Agent(1, 1, v1, "i")
    a2 = model.Agent(2, 1, v2, "j")
    a3 = model.Agent(3, 1, v3, "k")

    alloc = envy_allocation.EnvyAllocation.from_agents_items(set([a1, a2, a3]), set([a,b,c]))
    alloc.assign(c, a1)
    alloc.assign(a, a2)
    alloc.assign(b, a3)

    envy_dict = alloc._envy_dict()

    #act
    cycle = alloc._find_envy_cycle(a1, [], 3, envy_dict)

    #assert
    assert cycle == [a1, a2, a3]

def test_get_envy_cycle_simple():
    #arrange
    a = model.Item('a')
    b = model.Item('b')

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:2, b:1})

    v2 = model.AdditiveValuation()
    v2.provide_valuations({a:1, b:2})

    a1 = model.Agent(1, 1, v1)
    a2 = model.Agent(2, 1, v2)

    alloc = envy_allocation.EnvyAllocation.from_agents_items(set([a1, a2]), set([a,b]))

    alloc.assign(b, a1)
    alloc.assign(a, a2)

    #act
    cycles = alloc.get_envy_cycles()

    #assert
    cycle = [a1, a2]
    assert cycle in cycles
    cycles.remove(cycle)

    assert len(cycles) == 0

def test_get_envy_cycle_3_agents():
    #arrange
    a = model.Item('a')
    b = model.Item('b')
    c = model.Item('c')

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:2, b:1, c:1})

    v2 = model.AdditiveValuation()
    v2.provide_valuations({a:1, b:2, c:1})

    v3 = model.AdditiveValuation()
    v3.provide_valuations({a:1, b:1, c:2})

    a1 = model.Agent(1, 1, v1, "i")
    a2 = model.Agent(2, 1, v2, "j")
    a3 = model.Agent(3, 1, v3, "k")

    alloc = envy_allocation.EnvyAllocation.from_agents_items(set([a1, a2, a3]), set([a,b,c]))
    alloc.assign(c, a1)
    alloc.assign(a, a2)
    alloc.assign(b, a3)

    #act
    cycles = alloc.get_envy_cycles()

    #assert
    cycle = [a1, a2, a3]
    assert cycle in cycles
    cycles.remove(cycle)

    assert len(cycles) == 0

def test_get_envy_cycle_3_agents_2_cycles():
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

    alloc = envy_allocation.EnvyAllocation.from_agents_items(set([a1, a2, a3]), set([a,b,c]))
    alloc.assign(c, a1)
    alloc.assign(a, a2)
    alloc.assign(b, a3)

    #act
    cycles = alloc.get_envy_cycles()

    #assert
    cycle = [a1, a3]
    assert cycle in cycles
    cycles.remove(cycle)

    cycle = [a1, a2, a3]
    assert cycle in cycles
    cycles.remove(cycle)

    assert len(cycles) == 0

def test_get_envy_cycle_3_agents_weird_situation():
    #arrange
    a = model.Item("a")
    b = model.Item("b")
    c = model.Item("c")
    d = model.Item("d")
    e = model.Item("e")
    f = model.Item("f")

    v1 = model.AdditiveValuation()
    v1.provide_valuations({a:16, b:10, c:1, d:9, e:5, f:2})

    v2 = model.AdditiveValuation()
    v2.provide_valuations({a:11, b:4, c:10, d:10, e:16, f:9})

    v3 = model.AdditiveValuation()
    v3.provide_valuations({a:9, b:1, c:10, d:9, e:13, f:7})

    i = model.Agent(1, 1, v1, "i")
    j = model.Agent(2, 2, v2, "j")
    k = model.Agent(3, 3, v3, "k")

    alloc = envy_allocation.EnvyAllocation.from_agents_items(set([i, j, k]), set([a,b,c,d,e,f]))
    alloc.assign(a, i)

    alloc.assign(c, j)
    alloc.assign(f, j)

    alloc.assign(b, k)
    alloc.assign(d, k)
    alloc.assign(e, k)

    #act
    cycles = alloc.get_envy_cycles()

    #assert
    cycle = [j, k]
    assert cycle in cycles
    cycles.remove(cycle)

    assert len(cycles) == 0