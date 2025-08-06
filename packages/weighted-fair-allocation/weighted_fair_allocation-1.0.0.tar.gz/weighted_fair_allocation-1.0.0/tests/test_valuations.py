from weighted_fair_allocation import model

def test_ValuationCreation():
    v = model.Valuation()

    assert v.get_value(set()) == 0

def test_AddItemValuation():
    v = model.Valuation()

    item = model.Item("candy")

    v.add_valuation(set([item]), 5)

    assert v.get_value(set([item])) == 5

def test_AdditiveValuationCreation():
    v = model.AdditiveValuation()

    assert v.get_value(set()) == 0

def test_AddSingleItem():
    v = model.AdditiveValuation()

    item = model.Item("candy")

    v.add_valuation(item, 5)

    assert v.get_value(set([item])) == 5

def test_MultiItemAddition():
    v = model.AdditiveValuation()

    a = model.Item("a")
    b = model.Item("b")

    v.add_valuation(a, 1)
    v.add_valuation(b, 2)

    assert v.get_value(set([a, b])) == 3

def test_ProvideValuation():
    v = model.AdditiveValuation()

    a = model.Item("a")
    b = model.Item("b")

    v.provide_valuations({a: 1, b:2})

    assert v.get_value(set([a])) == 1
    assert v.get_value(set([a, b])) == 3

def test_get_preference_order():
    v = model.AdditiveValuation()

    a = model.Item("a")
    b = model.Item("b")
    c = model.Item("c")

    v.provide_valuations({a:3, b:2, c:1})

    assert v.get_preference_order() == [a,b,c]

def test_get_preference_order_tie_breaking():
    v = model.AdditiveValuation()

    a = model.Item("a")
    b = model.Item("b")
    c = model.Item("c")

    v.provide_valuations({a:2, b:2, c:3})

    assert v.get_preference_order() == [c,a,b]