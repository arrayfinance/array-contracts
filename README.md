[![MythXBadge](https://badgen.net/https/api.mythx.io/v1/projects/e81807aa-f119-456a-81b4-c88e493ddbf1/badge/data?cache=300&icon=https://raw.githubusercontent.com/ConsenSys/mythx-github-badge/main/logo_white.svg)](https://docs.mythx.io/dashboard/github-badges)

# Array Contracts

Repo for Array contracts.

## Contracts

#### Curve.sol v0.2
* [v0.1](https://etherscan.io/address/0xa0bc1aef5a4645a774bd38f4733c6c4b4a4b0d0a)
* [v0.2](https://etherscan.io/address/0xa3ad60f5142b8a54822d66bfa2f1f106e95ad8b0)
    * Fixed: broken `virtualLP` check in `buy()` 


#### ARRAY erc20
* [v0.1](https://etherscan.io/address/0x1bc65a16b8305c3186f88237c0adead145396de0)

#### Timelock
* [v0.1](https://etherscan.io/address/0x630db78131d3a67ab23900cd28165a99158fa6bc)

---

## Testing
The testing-suite is configured for use with [Ganache](https://github.com/trufflesuite/ganache-cli) on a [forked 
mainnet](https://eth-brownie.readthedocs.io/en/stable/network-management.html#using-a-forked-development-network).

To run the tests-

1. Install [Python 3.8](https://www.python.org/downloads/release/python-380/)
    - Linux: Refer to your distro documentation
    - [Mac installer](https://www.python.org/ftp/python/3.8.0/python-3.8.0-macosx10.9.pkg)
    - [Windows installer](https://www.python.org/ftp/python/3.8.0/python-3.8.0-amd64.exe)
2. Install python requirements
    - `pip3 install -r requirements.txt`
3. Install Node.js 10.x
    - Linux or Mac: via your [package manager](https://nodejs.org/en/download/package-manager/)
    - Windows: [x64 installer](https://nodejs.org/dist/latest-v12.x/node-v12.13.0-x64.msi)
    - Other [10.x downloads](https://nodejs.org/dist/latest-v12.x)
4. Install [Ganache](https://github.com/trufflesuite/ganache-cli)
    - `npm install -g ganache-cli@6.12.1`
5. [Install Yarn](https://classic.yarnpkg.com/en/docs/install)
6. [Install Black](https://pypi.org/project/black/)
    - `python3 -m pip install black`
7. Setup an account on [Etherscan](https://etherscan.io) and create an API key
    - Set `ETHERSCAN_TOKEN` environment variable to this key's value
        - Windows: `setx ETHERSCAN_TOKEN yourtokenvalue`
        - Mac/Linux: `echo "export ETHERSCAN_TOKEN=\"yourtokenvalue\"" | sudo tee -a ~/.bash_profile`
8. Setup an account on [Infura](https://infura.io) and create an API key
    - Set `WEB3_INFURA_PROJECT_ID` environment variable to this key's value
        - Windows: `setx WEB3_INFURA_PROJECT_ID yourtokenvalue`
        - Mac/Linux: `echo "export WEB3_INFURA_PROJECT_ID=\"yourtokenvalue\"" | sudo tee -a ~/.bash_profile`
9. Close & re-open your terminal before proceeding (to get the new environment variable values)
10. If you don't have git yet, go [set it up](https://docs.github.com/en/free-pro-team@latest/github/getting-started-with-github/set-up-git)
11. Pull the repository from GitHub and install its dependencies
    - `yarn install --lock-file`
        - You may have to install with `--ignore-engines` (try this if you get an error)
12. Run the test
    - `brownie test`
