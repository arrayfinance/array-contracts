import pytest


@pytest.fixture(scope='module')
def bancor(BancorFormula, accounts):
    bancor = accounts[0].deploy(BancorFormula)
    yield bancor


# paying y TOKENS for x arrayTokens, then selling x arrayTokens should give us back y Tokens.
def test_bancor_sanity(bancor):
    total_supply = 100
    poolbalance = 10
    cw = 1000000
    buy = 5

    purchase = bancor.calculatePurchaseReturn(total_supply, poolbalance, cw, buy)
    purchasev = purchase.return_value
    total_supply = total_supply + purchasev
    poolbalance = poolbalance + buy
    sale = bancor.calculateSaleReturn(total_supply, poolbalance, cw, purchasev)
    salev = sale.return_value
    assert salev == buy
