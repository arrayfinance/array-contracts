const { network: { provider }, expect, artifacts } = require('hardhat');
const fs = require('fs')

require('dotenv').config();

const Timelock = artifacts.require("ArrayTimelock");
const Curve = artifacts.require("Curve");
const ArrayToken = artifacts.require("ArrayToken");

async function main() {

    let DAO_MSIG = "0xB60eF661cEdC835836896191EDB87CC025EFd0B7";

    // deploy timelock
    let timelock = await Timelock.new(24*60*60, [DAO_MSIG], [DAO_MSIG]);
    console.log(timelock.address);

    // deploy curve
    let curve = await Curve.new();
    console.log(curve.address);

    // deploy array token
    let arrayToken = await ArrayToken.new("Array Token", "ARRAY");
    console.log(arrayToken.address);

}


main()
    .then(() => process.exit(0))
    .catch(error => {
        console.error(error);
        process.exit(1);
    });