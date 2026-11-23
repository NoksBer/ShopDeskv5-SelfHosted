# ShopDesk (NoksForge)

A self-hosted, multi-tenant repair shop manager. Python standard library only (3.11+). One SQLite database file per shop.

**Status: Phase 1 steps 1 to 4 are written but have NOT been run or tested yet** (no Python was available where they were written). See [ROADMAP.md](ROADMAP.md). [DESIGN.md](DESIGN.md) has the architecture and tenant-isolation strategy.

What exists: shop registration with a shop-type profile (computer, phone, bicycle, small engine, appliance, general, custom), staff sign-in with roles, business profile, team list, audit log, platform-admin tenant list/suspend, and a minimal responsive UI. Also: staff invites, customers and equipment (with shop-type-specific fields). Work tickets with configurable statuses, assignment and history. Technicians only see tickets assigned to them.

Version 3 adds: a drag-and-drop Kanban board of tickets (status columns, priority shown on every card), a due-date calendar, a services/pricing catalogue, parts inventory (cost, sale price, stock with an audit trail of every change), and invoices (add services, parts or custom lines; issue, print, mark paid, void). Issuing an invoice takes its parts out of stock; voiding puts them back. Existing businesses get the new permissions automatically on the next start; owners and managers get everything, front desk can create invoices, technicians can look up services and parts.

## Layout (same as Plateful)

```
install/shopdesk.sh   Proxmox helper script
server.py             entry point
shopdesk/             python package (app, auth, tenants, modules/, migrations/)
static/               frontend (index.html, app.js, style.css)
tests/                unittest suite
Dockerfile  DESIGN.md  ROADMAP.md  README.md
```

## Run locally

```bash
python3 server.py                            # http://127.0.0.1:8080, data in ./data
python3 server.py create-admin you@example.com   # optional platform administrator
python3 -m unittest discover -s tests -v     # run the tests
```

The first visit offers "Create business". After the first business exists, registration is closed unless `SHOPDESK_OPEN_SIGNUP=1`. Until then, whoever reaches the server first can create it, so do that before exposing the server.

## Configuration (environment variables)

| Variable | Default | Meaning |
|---|---|---|
| `SHOPDESK_HOST` / `SHOPDESK_PORT` | `127.0.0.1` / `8080` | Bind address (the installer sets `0.0.0.0`) |
| `SHOPDESK_DATA_DIR` | `./data` | Databases and uploads (`platform.db`, `tenants/<id>/tenant.db`) |
| `SHOPDESK_SECRET` | generated file `data/.secret` | Key for session-token hashes |
| `SHOPDESK_TRUST_PROXY` | `0` | `1` only behind your HTTPS proxy/tunnel: trusts `X-Forwarded-Proto/For`, `CF-Connecting-IP` |
| `SHOPDESK_OPEN_SIGNUP` | `0` | `1` lets anyone create a new business |
| `SHOPDESK_SECURE_COOKIES` | `0` | Force the Secure cookie flag (it is automatic behind an HTTPS proxy) |
| `SHOPDESK_SESSION_IDLE_SECONDS` / `_MAX_SECONDS` | `43200` / `604800` | Session idle and absolute lifetime |
| `SHOPDESK_REGISTER_LIMIT` | `5` | Business registrations per IP per hour |

## Install on Proxmox (helper script)

Run on the **Proxmox node shell**. Creates a Debian 12 LXC (2 cores, 1 GB RAM, 8 GB disk), installs ShopDesk as a systemd service under a non-root `shopdesk` user, and prints the URL. **Not yet run on a real Proxmox host.**

**Option A: from GitHub.** Push this folder to a repo, then run:

```bash
SHOPDESK_REPO=youruser/shopdesk bash -c "$(curl -fsSL https://raw.githubusercontent.com/youruser/shopdesk/main/install/shopdesk.sh)"
```

**Option B: no GitHub.** Copy `shopdesk.tar.gz` and `install/shopdesk.sh` to the node, then run:

```bash
SHOPDESK_TARBALL=/root/shopdesk.tar.gz bash /root/shopdesk.sh
```

Other modes (take the container ID):

```bash
bash shopdesk.sh update <CTID>             # takes a pre-update backup, keeps data, keeps previous code in /opt/shopdesk.prev
bash shopdesk.sh backup <CTID>             # consistent SQLite backup + uploads -> /var/lib/vz/dump
bash shopdesk.sh restore <CTID> <file>     # replaces data; old data folder is kept inside the container
```

Overrides: `CTID`, `CT_NAME`, `CORES`, `RAM`, `DISK`, `BRIDGE`, `STORAGE`, `TEMPLATE_STORAGE`, `PORT`, `BRANCH`, `TRUST_PROXY`, `BACKUP_DIR`.

Data lives in `/var/lib/shopdesk`. Config and secrets are in `/etc/shopdesk/shopdesk.env` (mode 640). Do not expose the plain HTTP port; use Cloudflare Tunnel and re-run with `TRUST_PROXY=1`.

## Known limitations

- Part labels: the barcode is Code 39 drawn by the browser. It has not been tried with real barcode scanners or label printers, so test one label before printing a batch. Choose your paper or label size in the browser's print dialog.

- Branding applies after sign-in only: the sign-in page itself shows the default ShopDesk look because the business isn't known yet. Logos are raster images (SVG is refused on purpose).
- Revenue months use the UTC date a payment was recorded, not the shop's timezone.

- Invoices: one tax rate per invoice, no partial payments, no emailing, no credit notes; "Mark paid" only records the date and method. Invoice and calendar dates use the server's date, not the shop's timezone.
- The board dragging uses pointer events (mouse and touch). On phones, hold the ⠿ handle or use the arrow buttons on each card.

- An email address can belong to one business only (staff login is by email alone).
- Rate limits are in memory (reset on restart; single process).
- Staff are added with invite links the owner copies and sends by hand (email delivery comes in Phase 2). There is no password reset yet.
- Admin-created tenants are not built; new businesses come from the registration form.
