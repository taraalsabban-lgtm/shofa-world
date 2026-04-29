# Threat Model

## Project Overview

This project is a standalone marketing website for the Shofa Podcast. It is implemented as a single static HTML page with inline CSS and JavaScript, plus a small Python `http.server` wrapper in `server.py` for local and deployed serving. There is no authentication or first-party backend business logic; the only dynamic data flow is from the browser directly to third-party services such as Formspree and YouTube.

Production scope for this scan is defined by the current deployment configuration in `.replit`, which points the public web root at the repository itself (`publicDir = "."`) and runs `python server.py`. Per platform assumptions, transport security is handled by the platform in production.

## Assets

- **Published site content and brand integrity** — the homepage, copy, imagery, and episode links represent the public brand.
- **Visitor-submitted contact data** — newsletter emails and guest-pitch form content are submitted from the browser to Formspree and may contain personal information.
- **Internal project artifacts** — repository metadata, archived site snapshots, attached notes, and operational files in the workspace should not be public unless intentionally published.
- **Operational metadata** — deployment configuration, repository remotes, and scan artifacts can help attackers map the environment even when no traditional application secrets are present.

## Trust Boundaries

- **Browser → Static host** — every request for HTML, images, archives, and hidden files crosses this boundary. The browser is untrusted and should only be able to fetch intentionally published assets.
- **Browser → Formspree** — newsletter and guest-pitch submissions are posted directly to Formspree from client-side JavaScript.
- **Browser → Third-party content** — the page embeds YouTube and loads third-party resources such as fonts; those integrations expand the client-side trust boundary.
- **Workspace/deployment boundary** — only curated public web assets should cross from the repository into the deployment’s web root. This is the highest-risk boundary in the current architecture.

## Scan Anchors

- **Production entry points:** `index.html`, `server.py`, `.replit`
- **Highest-risk code/config areas:** root-level static file serving in `server.py`; deployment config in `.replit`; client-side Formspree submissions in `index.html`
- **Public surfaces:** the entire site is public; there are no authenticated or admin-only routes
- **Usually dev-only areas:** `.git/`, `.local/`, `attached_assets/`, and `*.zip` archives should normally be non-public, but under the current deployment model they must be treated as production-reachable until proven otherwise

## Threat Categories

### Information Disclosure

The primary security risk in this project is accidental publication of repository contents rather than account takeover. The deployment must expose only the intended website assets. Hidden directories, repository metadata, archives, notes, and scan artifacts must not be reachable over HTTP, and directory listings must not reveal unpublished files.

### Tampering

This site has no first-party state-changing backend, so tampering risk is concentrated in client-side integrations. The page must only submit intended fields to Formspree, and public content must be served from a controlled asset set so attackers cannot use exposed deployment artifacts to replace, mirror, or manipulate site content.

### Denial of Service / Abuse

The public newsletter and guest-pitch forms can be targeted for spam or quota exhaustion because they submit directly to a third-party form backend. Abuse controls such as provider-side rate limiting, CAPTCHA, or origin restrictions are required outside the static site itself because there is no server-side gate in this repository.
