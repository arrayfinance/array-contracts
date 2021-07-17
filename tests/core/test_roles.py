import brownie
import pytest


def test_roles_on_chain(ArrayRoles, Contract, developer, daomsig, devmsig, user, accounts):
    roles = ArrayRoles.at('0x1c613e4F8DC1653c734cFB0De6e8add303166e77')
    dev_role = roles.DEVELOPER()
    daomsig_role = roles.DAO_MULTISIG()
    devmsig_role = roles.DEV_MULTISIG()
    developer = accounts.at('0x6d190a2e3eb0ebeea3ba663529a481212d2a4571', force=True)

    # check if the roles are set up correctly
    assert roles.hasRole(dev_role, developer)
    assert roles.hasRole(daomsig_role, daomsig)
    assert roles.hasRole(devmsig_role, devmsig)

    assert not roles.hasRole(daomsig_role, user)

    # devmsig is admin of developer role and can revoke / grantt
    roles.grantRole(dev_role, accounts[9], {'from': devmsig})
    assert roles.hasRole(dev_role, developer)
    assert roles.hasRole(dev_role, accounts[9])
    # daomsig is admin of all and can  revoke grant
    roles.grantRole(devmsig_role, accounts[8], {'from': daomsig})
    assert roles.hasRole(devmsig_role, devmsig)
    assert roles.hasRole(devmsig_role, accounts[8])


def test_roles(roles, daomsig, devmsig, user, accounts, developer):
    daomsig_role = roles.DAO_MULTISIG()
    devmsig_role = roles.DEV_MULTISIG()

    # check if the roles are set up correctly
    assert roles.hasRole(daomsig_role, daomsig)
    assert roles.hasRole(devmsig_role, devmsig)

    assert not roles.hasRole(daomsig_role, user)

    # daomsig is admin of all and can  revoke grant
    roles.grantRole(devmsig_role, accounts[8], {'from': daomsig})
    assert roles.hasRole(devmsig_role, devmsig)
    assert roles.hasRole(devmsig_role, accounts[8])
