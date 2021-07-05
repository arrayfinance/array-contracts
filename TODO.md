## TODO

### Primary
* [x] Make tests pass
    * [x] Fix npm vs. yarn redundancy
* [ ] Validate access control
* [x] [Deploy token contract](https://etherscan.io/address/0x1Bc65a16b8305C3186f88237C0AdeaD145396De0)
* [x] [Deploy curve contract](https://etherscan.io/address/0xa0bc1aef5a4645a774bd38f4733c6c4b4a4b0d0a)
* [ ] Deploy access control contract
W

### Other
* [ ] Determine order of deployment
    1. Deploy `ArrayTimelock.sol`
        * Args: 24 * 60 * 60 (1 day), [governance], [developer, user]
    2. Deploy `Curve.sol`
    2a. Copy Curve address to MINTER/BUNER roles in `ArrayToken.sol`
    3. Deploy 'ArrayToken.sol'
        * Args: "Array Token", "ARRAY"
    4. DAOMSIG to permit sending max amount of LP token to Curve