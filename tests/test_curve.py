import pytest
from brownie import Wei


@pytest.fixture( autouse=True )
def bancor(BancorFormula, owner):
    bancor = owner.deploy( BancorFormula )
    yield bancor


@pytest.fixture( autouse=True )
def isolation(fn_isolation):
    pass


# if we buy 1 ether worth of tokens, and then sell what we got, we should receive
# approx 1 ether back.
def test_bancor_formula(bancor, owner):
    total_supply = Wei( '2 ether' )
    poolBalance = Wei( '0.5 ether' )
    cw = 1000000
    buy = Wei( '1 ether' )
    purchase = bancor.calculatePurchaseReturn( total_supply, poolBalance, cw, buy )
    purchasev = purchase.return_value
    total_supply = total_supply + purchasev
    poolBalance = poolBalance + buy
    sale = bancor.calculateSaleReturn( total_supply, poolBalance, cw, purchasev )
    salev = sale.return_value
    assert salev / 1e18 == buy / 1e18
