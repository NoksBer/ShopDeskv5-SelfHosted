"""Permission catalogue and default role grants. The owner role implicitly has every permission."""

PERMISSIONS = [
    "business.manage",
    "users.manage",
    "users.read",
    "customers.read",
    "customers.write",
    "equipment.read",
    "equipment.write",
    "tickets.read",
    "tickets.write",
    "tickets.assign",
    "tickets.read_all",     # without it, a user only sees tickets assigned to them
    "audit.read",
    "services.read",
    "services.write",
    "inventory.read",
    "inventory.write",       # also reveals part costs
    "invoices.read",
    "invoices.write",
]

# (name, label, default permissions). Keep in step with migration 0005 for existing businesses.
ROLES = [
    ("owner", "Owner", list(PERMISSIONS)),
    ("manager", "Manager", [
        "users.read", "customers.read", "customers.write", "equipment.read", "equipment.write",
        "tickets.read", "tickets.write", "tickets.assign", "tickets.read_all", "audit.read",
        "services.read", "services.write", "inventory.read", "inventory.write", "invoices.read", "invoices.write",
    ]),
    ("technician", "Technician", [
        "customers.read", "equipment.read", "equipment.write", "tickets.read", "tickets.write",
        "services.read", "inventory.read",
    ]),
    ("front_desk", "Front desk", [
        "customers.read", "customers.write", "equipment.read", "equipment.write",
        "tickets.read", "tickets.write", "tickets.assign", "tickets.read_all",
        "services.read", "inventory.read", "invoices.read", "invoices.write",
    ]),
]

# Access levels a route may declare besides a permission name.
ACCESS_LEVELS = ("public", "authed", "platform")
