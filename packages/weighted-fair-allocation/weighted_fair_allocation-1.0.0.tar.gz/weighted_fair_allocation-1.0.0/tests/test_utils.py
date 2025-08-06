from weighted_fair_allocation import model, utils

def test_compute_possible_allocations_2_agents():
    #arrange
    a = model.Item('a')
    b = model.Item('b')
    c = model.Item('c')

    items = set([a,b,c])

    #act
    allocations = utils._compute_possible_splits(items, 2)

    #assert
    possibilities = [
        (frozenset(),         frozenset([a,b,c])),
        (frozenset([a]),      frozenset([b,c])),
        (frozenset([b]),      frozenset([a,c])),
        (frozenset([c]),      frozenset([a,b])),
        (frozenset([a,b]),    frozenset([c])),
        (frozenset([a,c]),    frozenset([b])),
        (frozenset([b,c]),    frozenset([a])),
        (frozenset([a,b,c]),  frozenset())
    ]

    for alloc in possibilities:
        assert alloc in allocations
        allocations.remove(alloc)

    assert len(allocations) == 0    

def test_compute_possible_allocations_without_empty_bundles_2_agents():
    #arrange
    a = model.Item('a')
    b = model.Item('b')
    c = model.Item('c')

    items = set([a,b,c])

    #act
    allocations = utils._compute_possible_splits_without_empty_bundles(items, 2)

    #assert
    possibilities = [
        # (frozenset(),         frozenset([a,b,c])),
        (frozenset([a]),      frozenset([b,c])),
        (frozenset([b]),      frozenset([a,c])),
        (frozenset([c]),      frozenset([a,b])),
        (frozenset([a,b]),    frozenset([c])),
        (frozenset([a,c]),    frozenset([b])),
        (frozenset([b,c]),    frozenset([a])),
        # (frozenset([a,b,c]),  frozenset())
    ]

    for alloc in possibilities:
        assert alloc in allocations
        allocations.remove(alloc)

    assert len(allocations) == 0  

def test_compute_possible_allocations_3_agents():
    #arrange
    a = model.Item('a')
    b = model.Item('b')
    c = model.Item('c')

    items = set([a,b,c])

    #act
    allocations = utils._compute_possible_splits(items, 3)

    #assert
    possibilities = [
        # 3, 0, 0
        (frozenset([a,b,c]),  frozenset(),          frozenset()),
        (frozenset(),         frozenset([a,b,c]),   frozenset()),
        (frozenset(),         frozenset(),          frozenset([a,b,c])),

        # 2, 1, 0
        (frozenset([a,b]),    frozenset([c]),   frozenset()),
        (frozenset([a,b]),    frozenset(),      frozenset([c])),
        (frozenset(),         frozenset([a,b]), frozenset([c])),
        (frozenset([c]),      frozenset([a,b]), frozenset()),
        (frozenset(),         frozenset([c]),   frozenset([a,b])),
        (frozenset([c]),      frozenset(),      frozenset([a,b])),

        (frozenset([a,c]),    frozenset([b]),   frozenset()),
        (frozenset([a,c]),    frozenset(),      frozenset([b])),
        (frozenset(),         frozenset([a,c]), frozenset([b])),
        (frozenset([b]),      frozenset([a,c]), frozenset()),
        (frozenset(),         frozenset([b]),   frozenset([a,c])),
        (frozenset([b]),      frozenset(),      frozenset([a,c])),

        (frozenset([b,c]),    frozenset([a]),   frozenset()),
        (frozenset([b,c]),    frozenset(),      frozenset([a])),
        (frozenset(),         frozenset([b,c]), frozenset([a])),
        (frozenset([a]),      frozenset([b,c]), frozenset()),
        (frozenset(),         frozenset([a]),   frozenset([b,c])),
        (frozenset([a]),      frozenset(),      frozenset([b,c])),

        # 1, 1, 1
        (frozenset([a]), frozenset([b]), frozenset([c])),
        (frozenset([a]), frozenset([c]), frozenset([b])),
        (frozenset([b]), frozenset([a]), frozenset([c])),
        (frozenset([b]), frozenset([c]), frozenset([a])),
        (frozenset([c]), frozenset([a]), frozenset([b])),
        (frozenset([c]), frozenset([b]), frozenset([a])),
    ]

    for alloc in possibilities:
        assert alloc in allocations
        allocations.remove(alloc)

    assert len(allocations) == 0   

def test_compute_possible_allocations_without_empty_bundles_3_agents():
    #arrange
    a = model.Item('a')
    b = model.Item('b')
    c = model.Item('c')

    items = set([a,b,c])

    #act
    allocations = utils._compute_possible_splits_without_empty_bundles(items, 3)

    #assert
    possibilities = [
        # 3, 0, 0
        # (frozenset([a,b,c]),  frozenset(),          frozenset()),
        # (frozenset(),         frozenset([a,b,c]),   frozenset()),
        # (frozenset(),         frozenset(),          frozenset([a,b,c])),

        # 2, 1, 0
        # (frozenset([a,b]),    frozenset([c]),   frozenset()),
        # (frozenset([a,b]),    frozenset(),      frozenset([c])),
        # (frozenset(),         frozenset([a,b]), frozenset([c])),
        # (frozenset([c]),      frozenset([a,b]), frozenset()),
        # (frozenset(),         frozenset([c]),   frozenset([a,b])),
        # (frozenset([c]),      frozenset(),      frozenset([a,b])),

        # (frozenset([a,c]),    frozenset([b]),   frozenset()),
        # (frozenset([a,c]),    frozenset(),      frozenset([b])),
        # (frozenset(),         frozenset([a,c]), frozenset([b])),
        # (frozenset([b]),      frozenset([a,c]), frozenset()),
        # (frozenset(),         frozenset([b]),   frozenset([a,c])),
        # (frozenset([b]),      frozenset(),      frozenset([a,c])),

        # (frozenset([b,c]),    frozenset([a]),   frozenset()),
        # (frozenset([b,c]),    frozenset(),      frozenset([a])),
        # (frozenset(),         frozenset([b,c]), frozenset([a])),
        # (frozenset([a]),      frozenset([b,c]), frozenset()),
        # (frozenset(),         frozenset([a]),   frozenset([b,c])),
        # (frozenset([a]),      frozenset(),      frozenset([b,c])),

        # 1, 1, 1
        (frozenset([a]), frozenset([b]), frozenset([c])),
        (frozenset([a]), frozenset([c]), frozenset([b])),
        (frozenset([b]), frozenset([a]), frozenset([c])),
        (frozenset([b]), frozenset([c]), frozenset([a])),
        (frozenset([c]), frozenset([a]), frozenset([b])),
        (frozenset([c]), frozenset([b]), frozenset([a])),
    ]

    for alloc in possibilities:
        assert alloc in allocations
        allocations.remove(alloc)

    assert len(allocations) == 0