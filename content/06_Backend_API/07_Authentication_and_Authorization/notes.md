# Authentication and Authorization

Identity and permissions are central to backend API design because they shape who can call the system and what those callers are allowed to do. This topic focuses on the conceptual split between proving identity and enforcing access rules correctly.

## Key Points

- **Authentication and authorization are different** - One establishes identity; the other decides permission.
- **Sessions and bearer tokens solve different problems** - Browser-centered apps and multi-client APIs often want different auth models.
- **JWTs are signed claims, not magic** - They carry header.payload.signature; still need short expiration, rotation, and a revocation strategy.
- **OAuth2 handles delegated access** - Authorization code flow for third-party logins; access tokens expire, refresh tokens renew them.
- **Passwords must be hashed** - Use argon2id or bcrypt; rate-limit login attempts; never reveal which field was wrong.
- **Roles are only one layer** - Real systems often need resource-level access checks too.
- **Frontend checks are not security** - The backend must enforce every protected rule itself.

## Example

```python
def can_view_order(user: dict, order: dict) -> bool:
    if user["role"] == "admin":
        return True
    return order["owner_id"] == user["id"]


user = {"id": 7, "role": "member"}
order = {"id": 42, "owner_id": 7}

print(can_view_order(user, order))
print(can_view_order({"id": 9, "role": "member"}, order))
```

The example separates identity from permission: both callers are authenticated users, but only one is authorized to access the specific order.
