"""Account store and authorization logic.

This code is NOT student-editable. It is kept separate from the verifier so the
grader can assess *validation* (did the verifier reject a bad token?) and
*permission* (does an authenticated principal get access?) independently.

Authorization rules:
  * The protected admin operation trusts the *verified* issuer's `role` claim.
  * The principal's `sub` must be an account that exists in the *current group*
    (the group is server-side context, never taken from the token or request).
  * A valid token for an unknown or other-group account gets no access (403).

HTTP mapping:
  * verification failure           -> 401 (invalid authentication)
  * authenticated but not allowed  -> 403 (valid auth, insufficient permission)
"""
from __future__ import annotations

from dataclasses import dataclass, field


class AuthzError(Exception):
    def __init__(self, status: int, reason: str) -> None:
        super().__init__(f"{status}: {reason}")
        self.status = status
        self.reason = reason


@dataclass
class Account:
    sub: str
    role: str  # "student" | "admin"
    password: str  # synthetic lab password
    group: str


@dataclass
class AccountStore:
    """Accounts across groups. `current_group` is the group this server
    instance serves; the admin resource is scoped to it."""
    current_group: str
    run_id: str
    accounts: dict[str, Account] = field(default_factory=dict)

    def add(self, account: Account) -> None:
        self.accounts[(account.group, account.sub)] = account

    def by_login(self, username: str, password: str) -> Account | None:
        acct = self.accounts.get((self.current_group, username))
        if acct is not None and acct.password == password:
            return acct
        return None

    def in_current_group(self, sub: str) -> Account | None:
        return self.accounts.get((self.current_group, sub))


def authorize_admin(validated_claims: dict, store: AccountStore) -> str:
    """Given already-validated claims, enforce group membership + admin role.

    Returns the group/run marker on success; raises AuthzError otherwise.
    Callers invoke this ONLY after the verifier has validated the token.
    """
    sub = validated_claims.get("sub")
    role = validated_claims.get("role")

    acct = store.in_current_group(sub) if isinstance(sub, str) else None
    if acct is None:
        # Authenticated, but the account is unknown or belongs to another group.
        raise AuthzError(403, "account not in this group")

    # The endpoint trusts the VERIFIED issuer's role assertion. The security
    # boundary is the verifier: if the token's signature/claims were validated,
    # its `role` is authoritative. This is exactly why the broken verifier is
    # exploitable (a forged `role` is trusted) and why repairing the verifier —
    # not this function — closes the hole.
    if role != "admin":
        raise AuthzError(403, "admin role required")

    return f"GROUP={store.current_group};RUN={store.run_id};ADMIN-OK"


def whoami(validated_claims: dict, store: AccountStore) -> dict:
    sub = validated_claims.get("sub")
    acct = store.in_current_group(sub) if isinstance(sub, str) else None
    if acct is None:
        raise AuthzError(403, "account not in this group")
    return {"sub": acct.sub, "role": acct.role, "group": acct.group}


def default_store(group: str = "group-01", run_id: str = "run-0001") -> AccountStore:
    """A small synthetic account set for a group."""
    store = AccountStore(current_group=group, run_id=run_id)
    store.add(Account(sub="alice", role="student", password="student-pw-alice", group=group))
    store.add(Account(sub="bob", role="student", password="student-pw-bob", group=group))
    store.add(Account(sub="root", role="admin", password="admin-pw-root", group=group))
    # An account in a DIFFERENT group, to test cross-group isolation.
    store.add(Account(sub="otheradmin", role="admin", password="x", group="group-99"))
    return store
