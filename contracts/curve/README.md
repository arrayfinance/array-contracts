# Bonding curve shiz


## BLOCKER: SMART POOL SETUP

## Todo
* [ ] Bonding curve template
* [x] Calculate curve based on pledged amount & start price
* [ ] Mint ARRAY
    * [ ] send 5% straight DAI to devs
    * [ ] mint Array with remaining 95%
    * [ ] 20% to Array Team vesting
    * [ ] 5% to Array DAO multisig (as treasury) (for airdrops and stuff)
    * [x] determine intervals to convert collateral deposited to other tokens (runs as Harvest)
    * [ ] Swap DAI for MultiAssets required by smart pool as a harvest 
    * [ ] Send LP to HoldingContract
* [x] Vault contracts
    * [x] Upgradable Proxy
    * [ ] Create Swap contract which swaps vault-generated interest into DAI, deposits into Smart Pool, refunds to user as claimable Array tokens, runs as a harvest

* [ ] HoldingContract AKA Burn ARRAY
    * [ ] Get fraction of array being burned, return proportional BPT to user who called it.

* [ ] DAO
    * [ ] Create DAO-Multisig controlled Balancer Smart Pool
    * [ ] Manually swap to Smart Pool weights and fill pool
    * [ ] Send BPT claim tokens to HoldingContract

* [ ] TOKEN
    * [ ] Mint 10,000 and send to DAO Multisig
    * [ ] Future mints are called from other contracts (Array Minting call with DAI, and Vault call for Swap)
    * Cap at 100k, governance removable.

* [ ] CURVE
    * [ ] Find nice curve candidates to test + share to DAO for voting

* [ ] Testing


## Specs
* 1m DAI pledged - 700k DAI collateral and 300k DAI to dev fund
    * Allocation of dev fund TBD
* 10k ARRAY given to pledgers
* 70% collateralized tokens
    * Start price = $100/ARRAY for 1m DAI pledged
* 100k max supply
* Quadratic curve
* When minting ARRAY
    * 70% straight to collateral
    * 30% to devs :)
* When burning ARRAY
    * 70% collateral returned
    * Price floor - if project shuts down, can still redeem for their collateral
    * max drawdown 30% of their collateral
* Tokens in collateral controlled by DAO
    * __Can__ put tokens into interest-bearing farms
    * __Can__ replace / exchange tokens
    * __Cannot__ remove tokens

## Breakdown of collateral
* 30% to devs (intial 300k DAI)

Remaining 70%: (want to be interest-bearing)
* 13.75% goes to renBTC
* 13.75% to WBTC
* 5% to ARRAY/ETH LP Tokens
    * Locks liquidity 
* 33.5% ETH
* 33.5% DAI

Converting collateral to interest-bearing will be expensive, so will be done in intervals.

Will be expensive converting collateral back when burning ARRAY... will send the interest tokens instead of selling to DAI first

## Future plans
* Earn interest from locked array tokens
    * Earned from their underlying collateral
