[![MythXBadge](https://badgen.net/https/api.mythx.io/v1/projects/e81807aa-f119-456a-81b4-c88e493ddbf1/badge/data?cache=300&icon=https://raw.githubusercontent.com/ConsenSys/mythx-github-badge/main/logo_white.svg)](https://docs.mythx.io/dashboard/github-badges)

# Array Contracts

### Deployed contracts
[Access Control](https://etherscan.io/address/0x1c613e4f8dc1653c734cfb0de6e8add303166e77#readContract)


Repo for Array contracts.

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
