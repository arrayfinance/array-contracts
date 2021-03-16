# Bonding curve shiz

## Todo
* [ ] Bonding curve template
* [ ] Calculate curve based on pledged amount & start price
* [ ] Mint ARRAY
    * [ ] split deposit to 70/30 collatoral/dev fund
    * [ ] determine intervals to convert collateral deposited to other tokens 
    * [ ] Split dev fund to non-interest bearing tokens
    * [ ] Split dev fund to interest bearing tokens
* [ ] Burn ARRAY
    * [ ] Refund 70% of collateral
    * [ ] Convert collateral to DAI first, or send as-is?
* [ ] DAO
    * [ ] Move tokens from one farm to another
    * [ ] Replace DAI for another stablecoin
    * [ ] Replace DAI with a volatile coin
    * [ ] Replace DAI with an interest-bearing coin
    * [ ] Replace DAI with multiple coins
    * [ ] Rebasing tokens?
    * [ ] Allocate dev funds
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
