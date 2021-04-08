import pytest


@pytest.fixture( scope='module', autouse=True )
def bancor(BancorFormula, deployer):
    bancor = deployer.deploy( BancorFormula )
    yield bancor


# paying y TOKENS for x arrayTokens, then selling x arrayTokens should give us back y Tokens.
def test_bancor_sanity(bancor):
    total_supply = 100
    poolBalance = 10
    cw = 1000000
    buy = 5

    purchase = bancor.calculatePurchaseReturn( total_supply, poolBalance, cw, buy )
    purchasev = purchase.return_value
    total_supply = total_supply + purchasev
    poolBalance = poolBalance + buy
    sale = bancor.calculateSaleReturn( total_supply, poolBalance, cw, purchasev )
    salev = sale.return_value
    assert salev == buy
