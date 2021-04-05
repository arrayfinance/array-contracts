import pytest
from rich.console import Console

console = Console()


@pytest.fixture( autouse=True )
def bancor(BancorFormula, owner):
    bancor = owner.deploy( BancorFormula )
    yield bancor


@pytest.fixture( autouse=True )
def isolation(fn_isolation):
    pass


# how much does it cost to buy 10k tokens
# starting with 0 supply and 0 collateral
def test_bancor_formula():
    # initially, when supply = 0 this is the formula

    reserve = 1 / 3
    slope = 1 / 1000000
    amount = 10000

    price = reserve * slope * (amount ** (1 / reserve))

    console.print( f'\n\n Price with reserveRatio of {reserve} , slope of {slope} is {price} for the first {amount} '
                   f'tokens\n' )

    reserve = 1 / 3
    slope = 3 / 1000000
    amount = 10000

    price = reserve * slope * (amount ** (1 / reserve))

    console.print( f'\n Price with reserveRatio of {reserve} , slope of {slope} is {price} for the first {amount} '
                   f'tokens\n\n' )


# paying y TOKENS for x arrayTokens, then selling x arrayTokens should give us back y Tokens.
def test_bancor_sanity(bancor):
    total_supply = 100
    poolBalance = 10
    cw = 1000000

    buy = 5

    purchase = bancor.calculatePurchaseReturn( total_supply, poolBalance, cw, buy )
    purchasev = purchase.return_value
    console.print( f'[red] Purchased: {purchasev}' )
    total_supply = total_supply + purchasev

    poolBalance = poolBalance + buy

    sale = bancor.calculateSaleReturn( total_supply, poolBalance, cw, purchasev )
    salev = sale.return_value
    console.print( f'[green] Sale: {salev}' )
    assert salev == buy
