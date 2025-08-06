import pytest

from weighted_fair_allocation import model
from weighted_fair_allocation.algorithms.weighted_adjusted_winner import WeightedAdjustedWinner
from weighted_fair_allocation.exceptions import InstanceError

@pytest.fixture()
def create_instance_cd_ab_split():
    a = model.Item('a')
    b = model.Item('b')
    c = model.Item('c')
    d = model.Item('d')

    v_i = model.AdditiveValuation()
    v_i.provide_valuations({a: 4, b:4, c:3, d:5})

    v_j = model.AdditiveValuation()
    v_j.provide_valuations({a:3, b:2, c:1, d:2})

    agent_i = model.Agent(1, 2, v_i)
    agent_j = model.Agent(2, 1, v_j)

    instance = model.Instance(set([agent_i, agent_j]), set([a, b, c, d]))

    return [agent_i, agent_j], [a,b,c,d], instance

@pytest.fixture()
def create_instance_bcd_a_split():
    a = model.Item('a')
    b = model.Item('b')
    c = model.Item('c')
    d = model.Item('d')

    v_i = model.AdditiveValuation()
    v_i.provide_valuations({a: 4, b:4, c:3, d:3})

    v_j = model.AdditiveValuation()
    v_j.provide_valuations({a:3, b:2, c:1, d:1})

    agent_i = model.Agent(1, 2, v_i)
    agent_j = model.Agent(2, 1, v_j)

    instance = model.Instance(set([agent_i, agent_j]), set([a, b, c, d]))

    return [agent_i, agent_j], [a,b,c,d], instance


def test_adjusted_winner_creation():
    # arrange
    item = model.Item('a')

    v1 = model.AdditiveValuation()
    v1.add_valuation(item, 1)

    a1 = model.Agent(1, 1, v1)
    a2 = model.Agent(2, 1, v1)
    a3 = model.Agent(3, 1, v1)

    #act
    valid = model.Instance(set([a1, a2]), set([item]))
    invalid = model.Instance(set([a1, a2, a3]), set([item]))

    #assert
    proc = WeightedAdjustedWinner(valid)
    with pytest.raises(InstanceError):
        proc = WeightedAdjustedWinner(invalid)


def test_adjusted_winner_item_order(create_instance_cd_ab_split):
    # arrange
    _, items, instance = create_instance_cd_ab_split

    a = items[0]
    b = items[1]
    c = items[2]
    d = items[3]

    adjWin = WeightedAdjustedWinner(instance)

    # act
    item_order = adjWin._calculate_item_order()

    # assert
    assert item_order == [c, d, b, a]

def test_adjusted_winner_item_order_tie_break():
    # arrange
    a = model.Item('a')
    b = model.Item('b')
    c = model.Item('c')
    d = model.Item('d')

    v_i = model.AdditiveValuation()
    v_i.provide_valuations({a: 4, b:3, c:2, d:1})

    v_j = model.AdditiveValuation()
    v_j.provide_valuations({a:4, b:3, c:2, d:1})

    agent_i = model.Agent(1, 2, v_i)
    agent_j = model.Agent(2, 1, v_j)

    instance = model.Instance(set([agent_i, agent_j]), set([a, b, c, d]))

    adjWin = WeightedAdjustedWinner(instance)

    #act
    item_order = adjWin._calculate_item_order()

    # assert
    assert item_order == [a,b,c,d]


def test_adjusted_winner_run_cd_ab_split(create_instance_cd_ab_split):
    #arrange
    agents, items, instance = create_instance_cd_ab_split

    a = items[0]
    b = items[1]
    c = items[2]
    d = items[3]

    a_i = agents[0]
    a_j = agents[1]

    adjWin = WeightedAdjustedWinner(instance)

    #assert
    allocation = adjWin.run()

    #act
    assert allocation[model.Agent.unassigned()] == set()
    assert allocation[a_i] == set([c, d])
    assert allocation[a_j] == set([a, b])

def test_adjusted_winner_run_bcd_a_split(create_instance_bcd_a_split):
    #arrange
    agents, items, instance = create_instance_bcd_a_split

    a = items[0]
    b = items[1]
    c = items[2]
    d = items[3]

    a_i = agents[0]
    a_j = agents[1]

    adjWin = WeightedAdjustedWinner(instance)

    #assert
    allocation = adjWin.run()

    #act
    assert allocation[model.Agent.unassigned()] == set()
    assert allocation[a_i] == set([b, c, d])
    assert allocation[a_j] == set([a])
    