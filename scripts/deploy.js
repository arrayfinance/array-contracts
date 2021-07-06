const { network: { provider }, expect, artifacts } = require('hardhat');
const fs = require('fs')

require('dotenv').config();

const Timelock = artifacts.require("ArrayTimelock");
const Curve = artifacts.require("Curve");
const ArrayToken = artifacts.require("ArrayToken");

async function main() {

    // deploy timelock
    // let timelock = await Timelock.new(24*60*60, [gov.address], [developer.address, user.address]);
    // console.log(timelock.address);

    // deploy curve
    let curve = await Curve.new();
    console.log(curve.address);

    // deploy array token
    // let arrayToken = await ArrayToken.new("Array Token", "ARRAY");
    // console.log(arrayToken.address);

}


main()
    .then(() => process.exit(0))
    .catch(error => {
        console.error(error);
        process.exit(1);
    });