require("@nomiclabs/hardhat-truffle5");
require("@nomiclabs/hardhat-waffle");
require("@nomiclabs/hardhat-web3");
require("@nomiclabs/hardhat-etherscan");


require("dotenv").config();

module.exports = {
    solidity: {
        compilers: [
            { version: "0.8.2" }
        ]
    },
    mocha: {
        timeout: 60000 // Here is 2min but can be whatever timeout is suitable for you.
    },
    networks: {
        hardhat: {
            forking: {
                url: `https://eth-mainnet.alchemyapi.io/v2/${process.env.ALCHEMY_KEY}`,
                accounts: [`${process.env.PRIVATE_KEY}`,]
            },
            gas: 'auto',
            blockGasLimit: 0x1fffffffffffff,
            allowUnlimitedContractSize: true,
            timeout: 1800000,
        },
        mainnet: {
            url: `https://eth-mainnet.alchemyapi.io/v2/${process.env.ALCHEMY_KEY}`,
            accounts: [process.env.PRIVATE_KEY]
        },

    },
    etherscan: {
        url: String(`https://eth-mainnet.alchemyapi.io/v2/${process.env.ALCHEMY_KEY}`),
        apiKey: process.env.ETHERSCAN_KEY
    },
    paths: {
        sources: "./contracts",
        tests: "./test",
        cache: "./cache",
        artifacts: "./artifacts"
    }
}