const { network: { provider }, expect, artifacts } = require('hardhat');
const fs = require('fs')

require('@nomiclabs/hardhat-ethers');
require("@nomiclabs/hardhat-truffle5");
require("@nomiclabs/hardhat-waffle");
require('dotenv').config();

const MyContract = artifacts.require("MyContract");

async function main() {
    let myContract = await MyContract.new();


}


main()
    .then(() => process.exit(0))
    .catch(error => {
        console.error(error);
        process.exit(1);
    });