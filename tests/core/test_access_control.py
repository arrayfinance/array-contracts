def test_timelock_roles(timelock, governance, developer, user):
    # sanity checks
    assert timelock.hasRole(timelock.PROPOSER_ROLE(), governance)
    assert not timelock.hasRole(timelock.PROPOSER_ROLE(), developer)
    assert timelock.hasRole(timelock.EXECUTOR_ROLE(), developer)
    assert timelock.hasRole(timelock.EXECUTOR_ROLE(), user)
    assert timelock.hasRole(timelock.TIMELOCK_ADMIN_ROLE(), timelock)

    # only timelock should be able to change roles
    assert timelock.getRoleAdmin(timelock.PROPOSER_ROLE()) == timelock.TIMELOCK_ADMIN_ROLE()
    assert timelock.getRoleAdmin(timelock.EXECUTOR_ROLE()) == timelock.TIMELOCK_ADMIN_ROLE()
    assert timelock.getRoleAdmin(timelock.TIMELOCK_ADMIN_ROLE()) == timelock.TIMELOCK_ADMIN_ROLE()


def test_proxy_admin_roles(proxy_admin, timelock):
    assert proxy_admin.owner() == timelock


def test_roles_roles(roles, governance, developer, timelock):
    assert roles.hasRole(roles.DEVELOPER(), developer)
    assert roles.hasRole(roles.GOVERNANCE(), governance)
    assert roles.hasRole(roles.TIMELOCK(), timelock)
    assert roles.hasRole(roles.DEFAULT_ADMIN_ROLE(), timelock)



