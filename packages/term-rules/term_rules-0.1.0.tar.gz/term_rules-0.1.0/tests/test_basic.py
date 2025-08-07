def test_rule_smoke():
    from term import Rule
    r = Rule(
        decision_rule=["CreditHistory <= 1.5"],
        decision_support=[0],
        identity=["node_0"]
    )
    assert r is not None
