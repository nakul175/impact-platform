# Choosing an email provider — decision pack for the owner

Prepared 2 October 2026 with build 0.26.0 plus the v0.27 email-readiness change (`docs/RELEASE-0.27-email.md`). Written for the person who has to decide, not for an engineer. Every fact taken from a provider's website is marked with the page it came from and the date it was read; anything we could not confirm on the provider's own pages is marked **unverified**. Prices change; check the linked page before signing up.

## 1. What this decision is, and what it is not

Today the platform's emails (invitations, recovery-contact codes) are written to a file on the server and never sent (`DEPLOYMENT-GUIDE.md` section 5). The software side of sending is now done: the worker speaks SMTP with STARTTLS and a username and password, verifies the provider's certificate, keeps to a sending limit you set, and `deploy/mail-check.sh` sends a test message and shows the conversation. What is missing is three things only you can provide:

1. **A domain name you control** to send from. The current address, `168-144-78-191.sslip.io`, is a convenience name whose DNS we cannot edit, and no provider will let you send as it. Use a subdomain of a domain you own, for example `impact.aplyd.com`, with the address `no-reply@impact.aplyd.com`. A subdomain keeps the platform's sending reputation separate from your main company mail.
2. **An account with one provider**, with the sending domain verified there.
3. **Four DNS records** on that subdomain (section 4). Nothing can be switched on before they exist.

This decision does not cover marketing mail or newsletters (the platform sends none), and it does not by itself give you "Forgot password" on the sign-in page: Keycloak sends those emails through its own, separate SMTP setting (section 7).

## 2. The three candidates

All three work from India in the sense that matters here: the server (a DigitalOcean droplet in Bangalore) connects out to the provider over SMTP port 587 with STARTTLS, and none of them restricts where the sending server is. Volume will be small for a long time (tens to a few hundred emails a month), so the entry tier is what counts.

| | Amazon SES | Postmark | Brevo |
|---|---|---|---|
| What it is | Part of AWS; pay per email | Transactional-only specialist | Marketing suite with a transactional SMTP relay |
| Entry cost | $0.10 per 1,000 emails ("à la carte"); new AWS accounts get up to $200 of credits for 6 months ([pricing page](https://aws.amazon.com/ses/pricing/), read 2 Oct 2026). A Mumbai region exists (`email-smtp.ap-south-1.amazonaws.com`, [endpoint list](https://docs.aws.amazon.com/general/latest/gr/ses.html), read 2 Oct 2026) | Free developer allowance of 100 emails a month, no overage; first paid plan $15 a month for 10,000 emails, $1.80 per extra 1,000 ([pricing page](https://postmarkapp.com/pricing), read 2 Oct 2026) | Free plan: up to 300 emails a day once sending is approved; SMTP relay included on every plan; the free plan adds a Brevo logo to emails, removed on the paid "Starter" plan ([pricing page](https://www.brevo.com/pricing/), read 2 Oct 2026). Starter price: about $9 a month according to third-party reviews — **unverified** on Brevo's own page, which did not show the figure |
| Monthly cost at our volume | Effectively zero (a few hundred emails cost cents; AWS bills the account in INR with GST when it is an Indian account — **unverified**) | $0 on the developer allowance until more than 100 emails a month, then $15 | $0, with a Brevo logo in every email; about $9 to remove it (**unverified** figure) |
| SMTP details | Ports 25, 587 or 2587 for STARTTLS ([SMTP guide](https://docs.aws.amazon.com/ses/latest/dg/smtp-connect.html), read 2 Oct 2026). SMTP credentials are separate from AWS access keys and are created in the SES console (**unverified** here; from memory of the SES documentation) | `smtp.postmarkapp.com`, ports 25, 2525 or 587, STARTTLS; the username and password are an SMTP token's access key and secret key, or the server API token for both ([SMTP guide](https://postmarkapp.com/developer/user-guide/send-email-with-smtp), read 2 Oct 2026) | `smtp-relay.brevo.com`, port 587, login and an SMTP key — **unverified** (not read on Brevo's pages during this review) |
| Setup effort | Highest: an AWS account, a region, domain verification, then a request to leave the "sandbox" (new accounts can only send to verified addresses until AWS approves production access — **unverified** wording, well known) | Lowest: sign up, verify the domain, create a server and an SMTP token. New accounts are reviewed before they may send to addresses outside the own domain (**unverified**) | Low: sign up, verify the domain, request sending approval (the pricing page says sending starts "once account approval for sending is granted") |
| Bounce and delivery information | Available by webhook or SNS; not built into the platform yet (section 6) | Event webhooks included on every plan (pricing page); not built into the platform yet | Outbound webhooks included (pricing page); not built into the platform yet |
| Where data is processed | Region of your choice, Mumbai included | United States (**unverified**) | European Union (**unverified**) |
| Risk to watch | Account complexity; a mis-set region or IAM policy is the usual failure | A free allowance of 100 a month is tight once several organisations are onboarded; the step to $15 is small | A marketing product; the free plan's logo looks unprofessional in an invitation; daily cap of 300 |

## 3. Recommendation

**Postmark** for the first year: least setup, transactional only, clear event webhooks when we build bounce handling, and the price is $0 until the platform sends more than 100 emails a month, then $15. If you already run other systems on AWS and want one bill, **Amazon SES in Mumbai** is the cheaper long-term choice at the cost of a longer setup (sandbox exit, SMTP credentials, region). Brevo is the fallback if you want zero cost with no limit on monthly volume and accept the logo.

Whichever you choose, the platform's configuration is the same five values (section 5); switching provider later is a change of those values and the DNS records, not a software change.

## 4. DNS records on the sending domain

Assume the sending subdomain is `impact.aplyd.com` and the From address `no-reply@impact.aplyd.com`. Records are added at the DNS host of `aplyd.com` (wherever its name servers are managed). The exact values for DKIM come from the provider's domain-verification screen; the shapes below are what to expect.

1. **SPF** — a TXT record on `impact.aplyd.com` naming the provider as allowed to send for it. One record only; if one already exists, merge the `include:` into it.
   - SES: `v=spf1 include:amazonses.com -all`
   - Postmark: `v=spf1 include:spf.mtasv.net -all` (**unverified** value; take it from Postmark's domain screen)
   - Brevo: `v=spf1 include:spf.brevo.com -all` (**unverified** value; take it from Brevo's domain screen)
2. **DKIM** — the provider signs each email and publishes the public key through records you add. SES "Easy DKIM" gives three CNAME records (`<token>._domainkey.impact.aplyd.com`); Postmark gives one TXT record (`<selector>._domainkey.impact.aplyd.com`); Brevo gives its own set. Copy them exactly; the provider's screen turns green when it sees them (minutes to a few hours).
3. **DMARC** — a TXT record on `_dmarc.impact.aplyd.com` that tells receivers what to do when SPF or DKIM fails and where to send reports. Start in monitoring mode: `v=DMARC1; p=none; rua=mailto:dmarc@aplyd.com`. After two to four weeks of clean reports move to `p=quarantine`, later `p=reject`. Without DMARC, Gmail and Microsoft treat mail from a new domain with suspicion.
4. **Return-Path (bounce) domain**, optional but recommended: SES calls it a custom MAIL FROM domain (an MX and a TXT record on `bounce.impact.aplyd.com`); Postmark a custom Return-Path (a CNAME `pm-bounces.impact.aplyd.com` → `pm.mtasv.net`, **unverified** target; take it from the screen). It makes SPF "align" with the From domain, which DMARC wants.

Steps, in order: (a) choose the subdomain and From address; (b) create the provider account and add the domain there; (c) add the DNS records it shows, plus DMARC; (d) wait until the provider shows the domain as verified; (e) only then do section 5.

## 5. Switch-over on the server (about fifteen minutes)

Everything is done in the server console as root. No code changes.

1. Put the non-secret values in `/opt/impact/config.env` (create the file if it does not exist, `KEY=value` lines):
   ```
   SMTP_HOST=smtp.postmarkapp.com          # or email-smtp.ap-south-1.amazonaws.com, smtp-relay.brevo.com
   SMTP_PORT=587
   SMTP_USERNAME=<the SMTP username or access key the provider gave you>
   SMTP_FROM=no-reply@impact.aplyd.com
   EMAIL_RATE_LIMIT=200                    # at most this many emails per window from this server
   EMAIL_TENANT_RATE_LIMIT=50              # and this many per organisation (tenant) per window
   EMAIL_RATE_WINDOW_SECONDS=60
   ```
   `SMTP_STARTTLS` stays at its default `auto`: encryption with certificate verification is mandatory for any provider and cannot be switched off. The rate limits are for the provider's benefit (every provider caps new accounts); the worker never gives up on an email because of them, it only waits.
2. Put the password in `/opt/impact/secrets.env` (one line, `SMTP_PASSWORD=<the secret the provider gave you>`). That file is root-only and its values are blanked from every log and status page; `config.env` is not.
3. Regenerate the environment and restart the worker:
   ```
   sudo /opt/impact/repo/deploy/update.sh
   sudo docker compose -p impact -f /opt/impact/repo/deploy/compose.yaml --env-file /opt/impact/compose.env up -d worker
   ```
   (The deployment script — also run automatically every three minutes — rewrites `compose.env` on every run but recreates containers only for a new commit, hence the second command.)
4. Send a test message to yourself: `sudo /opt/impact/repo/deploy/mail-check.sh you@aplyd.com`. The transcript must show `STARTTLS`, a `235` reply (authentication accepted) and a `250` after the message. Passwords never appear in it. Open the message and check its headers: `DKIM: PASS` and `SPF: PASS` (Gmail: "Show original").
5. Invite a test person from the platform and watch **Tenant lifecycle → Workers**: the delivery should show as sent within a minute. `https://<app>/deploy-status.json` raises `DELIVERIES_DEAD` if the provider refuses messages for good.
6. To go back to capture-only (for example while a provider problem is investigated): remove `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME` from `config.env`, `SMTP_PASSWORD` from `secrets.env`, and repeat step 3.

## 6. What stays unsolved after the switch

- **Bounces after acceptance are invisible.** The platform learns only what the provider says during the SMTP conversation (a `5xx` reply becomes a DEAD delivery an operator can see). An email the provider accepts and then cannot deliver (mailbox full, address gone) is reported by the provider on its dashboard and by webhook; **the webhook is not built**. Until it is, someone must look at the provider's dashboard when a person says they received nothing. The design for it is in `docs/RELEASE-0.27-email.md`.
- **No inbound email.** Replies to `no-reply@` go nowhere; the message text says so. Support requests still travel outside the platform.
- **Limits are per worker process.** The deployment runs one worker, so the limits in `config.env` are the limits the provider sees. A second worker would double them.
- **Sender reputation is yours to earn.** A new domain starts cold; keep DMARC in monitoring mode first and do not send from it for anything else.
- **Provider outage.** The worker retries each email with growing delays, six attempts over roughly a quarter of an hour, then marks it DEAD; an operator re-queues DEAD deliveries from the Workers panel once the provider is back. A longer outage therefore needs that manual step.

## 7. Keycloak's own email ("Forgot password")

The sign-in service sends password-reset and verification emails itself, through an SMTP setting inside the Keycloak realm, not through the platform's worker. It is currently empty, which is why "Forgot password" is switched off. The same provider account can be used: in the Keycloak admin console (`https://auth.<app>/admin/`, realm `impact`, **Realm settings → Email**) enter the same host, port 587, "Enable StartTLS", "Enable authentication" with the same username and password, and the From address. This is a manual step today; making `update.sh` set it from `config.env` is listed in the release note as follow-up work.

## 8. Facts we did not verify, in one place

Postmark's data location and the exact SPF `include:` and Return-Path targets; Brevo's Starter price, SMTP host and SPF value; AWS billing in INR with GST for an Indian account; the SES sandbox rule and the way SES SMTP credentials are created; whether Postmark reviews new accounts before allowing external recipients. Each is marked **unverified** above and is confirmed in the provider's own screens during setup; none changes the recommendation.
