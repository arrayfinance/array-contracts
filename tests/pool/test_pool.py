import pytest


@pytest.fixture()
def deployer():
    from scripts.deployer import Deployer
    d = Deployer()
    d.setup()
    yield d


# puts 100 DAI in and gets some pool tokens out
def test_pool_in(deployer):
    before = deployer.pool.balanceOf(deployer.me)
    deployer.tokens.dai.approve(deployer.pool, 100e18)
    tx = deployer.pool.joinswapExternAmountIn(deployer.tokens.dai.address, 100 * 1e18, 0)
    after = deployer.pool.balanceOf(deployer.me)
    assert tx.return_value == after - before
