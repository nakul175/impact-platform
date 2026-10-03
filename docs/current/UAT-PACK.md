# Release 1 user-acceptance test pack

Build 0.25.0 (schema 27, domain API 1.15.0, platform API 1.6.0), prepared 1 October 2026 for Release 1 *Usable core* (scope decision SD-01, [delivery plan](../DELIVERY-PLAN.md) §2). This pack is written for the programme owner and the people they ask to test. It does not accept anything: passing a scenario here is evidence for step 3 of the [release acceptance procedure](RELEASE-ACCEPTANCE.md) ("Execute UAT with representative authorized users and independent control reviewers"), and the release decision is still taken and signed separately. What still blocks acceptance is listed in [RELEASE-1-ACCEPTANCE-GAPS.md](RELEASE-1-ACCEPTANCE-GAPS.md).

Use synthetic data only: the sample names, districts and numbers below are invented. Never type real personal data into the staging server or a local workspace (repository rule 11).

## 1. Read this first: two places to test

**Build 0.26.0 update (v0.26a *Usable staging*, `docs/RELEASE-0.26a.md`).** The three staging limits listed below were removed by build 0.26.0 for tenants onboarded after it is deployed: reference data is created from **People & access → Reference data** (one click for the standard set), new tenants receive the `initial-access-v2` package (every implemented capability, purpose-required ones only as purpose-bound grants from **Purpose-bound access**), and a second platform operator is nominated, given a sign-in and accepted from **Tenant lifecycle → Platform operators**, with no droplet console step. The owner's click-path is `docs/current/DEPLOYMENT-GUIDE.md` §4.1. A tenant that already applied the old package keeps it. The scenarios below were written for build 0.25.0 and have not been rewritten; until they are, run staging onboarding from the deployment guide and the measurement cycle on either track.

**Build 0.27.0 update (`docs/RELEASE-0.27.md`).** A5 is resolved: an imported value's source key is `<unit key>/<indicator id>/<period id>` and the import preview shows each value's key and whether the approved plan names it ("(planned)" / "(unplanned)"). To close a period that receives imports, first add the import units to the indicator's collection plan as obligations with namespace `IMPORT` and key `<unit key>/<indicator id>/<period id>` (or amend the plan afterwards through **Change requests**, independently approved), then import, approve, calculate and close. Values the plan does not name still block close (`UNPLANNED_VALUES`), as scenario 9 notes. Organisations onboarded before 0.27.0 keep the capability ceiling they were given; do not create a second reporting calendar in a UAT tenant unless the scenario needs it. Since build 0.27.0 the tenant-lifecycle change forms open as dialogs, and an owner without access yet sees a waiting page instead of an error.

Before build 0.26.0, a tenant created on the staging server through the proper onboarding steps **cannot run the measurement cycle**. This was checked in the code on 1 October 2026:

- No screen or API creates a reporting calendar, a reporting period, a review (workflow) template or a report template. These exist only in the synthetic fixture loaded into local workspaces. Without a workflow template an observation cannot be submitted for review; without a calendar and periods there is nothing to collect against, target or close; without a report template no report can be drafted.
- The access package an owner receives at onboarding (`apps/api/impact_api/bootstrap_profile.json`, unchanged since build 0.12) sets the ceiling of what administrators can ever delegate. It does not contain the capabilities of anything built since build 0.18: results framework, targets, forms, imports, evidence uploads, dashboards, report exports, report publication and withdrawal, disclosure requests, audit export and data-subject requests (48 capabilities in total, listed in the gaps document). Custom roles cannot exceed that ceiling.
- Only one platform operator exists on staging, and activating a tenant needs a second operator who neither requested the tenant nor owns it.

So this pack uses two environments:

| Track | Where | Who runs it | Used for |
|---|---|---|---|
| **S — staging** | https://168-144-78-191.sslip.io with real sign-in (Keycloak, authenticator app) | The owner and named testers, from their own computers; the owner uses the DigitalOcean droplet console for account tasks | Sign-in, onboarding, access administration, operations and support checks (scenarios 1–5, 20–21) |
| **L — local UAT workspace** | An engineer's computer running `make dev` with the synthetic fixture tenant, shared on screen or used at that computer | An engineer sets it up and signs testers in; testers perform every step themselves | The full measurement and reporting cycle (scenarios 6–19, 22), until the staging gaps are closed |

A scenario passed on Track L shows the behaviour of the build, not that the hosted service is usable by your organisation. Record the track with every result. When the gaps above are closed, repeat scenarios 6–19 on Track S before signing the release.

## 2. How to record a result

For every scenario write down: tester name and role account used, date and time (UTC), track, build and commit (Track S: the `commit` field of https://168-144-78-191.sslip.io/deploy-status.json; Track L: the engineer reads `VERSION.json` and `git rev-parse HEAD`), the outcome, and for any failure the **correlation ID** shown with the error message or returned in the error response. Tick **Pass** only when every expected result is seen. A step that cannot be performed is a **Fail** with the reason, not a skip. Do not paste passwords, one-time codes, invitation links or screenshots of them into the record (see the [support runbook](SUPPORT-RUNBOOK.md) §7).

Each scenario names the requirement IDs it exercises (FSD v1.1 identifiers; their current status is in the [completion ledger](../COMPLETION-LEDGER.md)) and, where it applies, the BRD acceptance scenario (UAT01–UAT30, FSD AT01–AT30) it covers in part. No scenario here covers a BRD scenario completely.

## 3. Accounts you need

The platform requires different natural persons for authoring and approving, for requesting and activating a tenant, and for proposing and approving access. One person with several logins does not count as several people. Plan for at least six real people on Track S.

| Role in this pack | Track S: how the account is created today | Track L: fixture account |
|---|---|---|
| **Owner of the deployment, first platform operator** | Created by the deployment for the address in `IMPACT_OWNER_EMAIL` (default nakul.jain@aplyd.com). In the droplet console: `sudo /opt/impact/repo/deploy/first-admin.sh` shows the one-time password; first sign-in sets a password and an authenticator app ([deployment guide](DEPLOYMENT-GUIDE.md) §4). | `owner` (also a platform operator) |
| **Second platform operator** (needed to activate a tenant the first operator requested) | **Not possible with the console scripts.** `scripts/bootstrap_operator.py operator` refuses once any operator exists and there is no operator-management screen; a second operator is a deliberate database change by the owner, not automated in this build. Scenario 2 stops at activation until this exists. | `admin` (also a platform operator in the local workspace) |
| **Tenant owner** (accepts custody; must not be the requesting operator) | Console: `sudo /opt/impact/repo/deploy/add-user.sh name@example.org "First" "Last"`; hand over the one-time password; the person signs in once (sets password and authenticator) before being named. | `author` (in the README onboarding walk-through) |
| **Second administrator** (accepts the initial access package) | `add-user.sh` as above, then signs in once. | `reviewer` |
| **Recovery contact** (a person other than the owner) | `add-user.sh` as above, then signs in once. | `partner` |
| **Author / programme manager** | `add-user.sh`, sign in once, then invited into the tenant (scenario 5) and given the AUTHOR and PROGRAMME_MANAGER roles by access request. | `author` (holds AUTHOR, PROGRAMME_MANAGER and REVIEWER, so self-approval is refused for independence, not for lack of a role) |
| **Independent reviewer** | `add-user.sh`, sign in once, invited, REVIEWER role by access request. | `reviewer` |
| **Enumerator** | `add-user.sh`, sign in once, invited. There is no ENUMERATOR role in the staging access package and form capabilities are outside its ceiling, so an enumerator cannot be given form access on staging today. | `enumerator` (submits unbound forms only) |
| **Privacy officer** | Not possible on staging: no screen or API issues the purpose-bound (`DATA_SUBJECT_REQUEST`) grants that privacy cases need. | `privacy` (approves and executes) and `admin` (records the request) |
| **Named recipient of a publication** | Any active member of the tenant. | `partner` |
| **Other tenant** (for "cannot see" checks) | A second tenant, which needs the second operator. | `other_tenant` |

Everyday account tasks on staging (all in the droplet console as root): `list-users.sh` lists accounts and their state; `reset-user.sh <email>` issues a new one-time password and lifts a lockout; `reset-user.sh <email> --totp` also removes a lost authenticator. A one-time password is shown once, on screen only; hand it over in person or by phone, never by e-mail or chat. Each person's platform identity UUID, which the onboarding screens ask for, is in the console log line `added <email> (… identity <uuid>)`: `sudo grep '<email>' /opt/impact/state/admin-actions.log`. An identity UUID is not a secret.

**Track L set-up (engineer).** `make setup`, then `make dev` (or `.venv/bin/python scripts/run.py dev --ephemeral` for a workspace that is discarded on shutdown). Open http://127.0.0.1:8000. Every fixture account's password is in `.local/dev/passwords.json`; type it for the tester, do not show or send the file. Invitation and recovery e-mails go to `.local/dev/synthetic-mail.jsonl`. The fixture tenant holds a seeded indicator, a reporting calendar with period **2026-Q3** (1 July to 1 October 2026), review templates, a report template and a synthetic OFFICIAL 46.36 result that is fixture data, not a calculation by this build. Fixture authority expires on 2027-09-01.

## 4. Scenarios

### Scenario 1 — Sign in with two factors, step up and sign out (Track S)

Requirements: FR-IAM-002, FR-IAM-003, FR-IAM-006. BRD: none directly.

1. On your own computer open https://168-144-78-191.sslip.io/ and choose **Sign in**. You are sent to `auth.168-144-78-191.sslip.io`.
2. Enter your e-mail and password, then the 6-digit code from your authenticator app.
3. Wait more than five minutes, then try an administrative action (for example invite a member in scenario 5).
4. Choose **Sign out**.
5. Enter a wrong password five times in a row on the sign-in page.

Expected: step 2 returns you to the platform signed in; step 3 asks you to sign in again before the action is accepted (fresh assurance is five minutes); step 4 ends both the platform session and the sign-in service session (the next **Sign in** asks for the password again); step 5 locks the account for a while, and `list-users.sh` in the console shows it as locked until `reset-user.sh` lifts it.

Result: [ ] Pass [ ] Fail — notes:

### Scenario 2 — Tenant onboarding and activation (Track S; Track L as fallback)

Requirements: FR-TEN-001, FR-ACC-004. BRD: none directly.

1. As the first operator open **Tenant lifecycle** (sidebar, under the main navigation) and create a **New tenant request**: operating name `UAT Synthetic Trust`, the tenant owner's identity UUID, the offered qualified deployment (region `do-blr1`, privacy reference `staging-privacy-notice-v1`).
2. As the tenant owner, sign in, open **Tenant lifecycle**, review the request and choose **Accept ownership**.
3. As the first operator, try **Activate tenant** on the request you made yourself.
4. Complete scenario 4 (recovery contact), then as the **second operator** choose **Activate tenant**.

Expected: step 1 creates a Requested record and gives nobody business access; step 2 records acceptance only; step 3 is refused because the requester cannot activate (independence); the readiness checks list what is missing; step 4 makes the tenant Active, still with no business grants. On Track S, step 4 cannot be performed until a second operator exists — record **Fail: blocked (no second operator)**. On Track L follow the README walk-through: `admin` requests, `author` accepts, `partner` is the recovery contact, `admin` approves the contact, `owner` activates.

Result: [ ] Pass [ ] Fail — notes:

### Scenario 3 — Initial access for the owner and a second administrator (Track S after scenario 2; Track L)

Requirements: FR-TEN-001, FR-IAM-009, FR-ACC-004. BRD: none directly.

1. As the tenant owner open **Tenant lifecycle → Initial access**, choose **Propose initial access**, name the second administrator's identity UUID, an expiry within 90 days and the roles to make delegable (AUTHOR, REVIEWER, PROGRAMME_MANAGER at least).
2. As the second administrator choose **Accept administrator role**.
3. As an operator who is neither the owner nor the second administrator choose **Approve initial access**.
4. Return to the workspace and select the new tenant.

Expected: before step 3 nobody has access; after it the owner and the second administrator see **People & access** and can administer members, but neither has programme-data access yet. A second provision attempt is refused (one-time). An approver who is the owner or the second administrator is refused.

Result: [ ] Pass [ ] Fail — notes:

### Scenario 4 — Recovery contact (Track S; Track L)

Requirements: FR-TEN-001, FR-TEN-010. BRD: none directly.

1. As the tenant owner open **Tenant lifecycle → Recovery contacts** and **Nominate recovery contact** (the contact's identity UUID, an expiry within 90 days, a reason).
2. As the contact choose **Verify my recovery contact** within seven days.
3. Optional: as the contact choose **Email me a verification code**. On Track S the code is captured on the server, not delivered (no e-mail provider); the owner reads it in the console (deployment guide §5) and gives it to the contact in person. Enter it with **Enter verification code** within 15 minutes.
4. As an operator who is neither the owner nor the contact, choose **Approve recovery contact** within 24 hours of the verification.

Expected: the contact becomes Active and counts for readiness; the contact gains no access, no reset right and no custody. The owner or the contact cannot approve their own nomination. A wrong code five times locks that code.

Result: [ ] Pass [ ] Fail — notes:

### Scenario 5 — Members, invitations and grants (Track S after scenario 3; Track L)

Requirements: FR-IAM-001, FR-IAM-008, FR-IAM-009, FR-ACC-001, FR-ACC-003, FR-ACC-004. BRD: UAT11 (part), UAT12 (part).

1. As an administrator open **People & access → Invitations** and invite the author's e-mail with role **AUTHOR**, scope **All workspace records**, the default expiry and a reason. Copy the **Invitation link** shown on screen.
2. Give the link to the author in person (on staging the invitation e-mail is captured on the server, not delivered). The author opens it while signed in and joins.
3. Have the same link opened while signed in as a different person.
4. As the requesting administrator open the new member and request the **REVIEWER** role; then try to approve that request yourself under **Access requests**.
5. As the other administrator approve it.
6. Suspend the member, try to use the workspace as that member, then reactivate.
7. As a member of another tenant (Track L: `other_tenant`), try to open a record of this tenant by its address.

Expected: step 2 creates exactly one membership; step 3 is refused (the link is bound to the intended person); step 4's self-approval is refused; step 5 adds the role without replacing earlier grants; step 6 blocks access during suspension and requires a new sign-in after reactivation; step 7 answers "not available", the same as a record that does not exist.

Result: [ ] Pass [ ] Fail — notes:

### Scenario 6 — Programme and indicator set-up (Track L)

Requirements: FR-PRG-001, FR-IND-001, FR-IND-002, FR-IND-008, FR-IND-012, FR-PLN-006. BRD: UAT25 (the "reviewed valid definition before activation" part only).

1. As `author` open **Portfolio** and create programme `UAT Water Access` with dates covering 2026-Q3, the seeded reporting calendar and the demonstration geography.
2. Open **Measurement setup → Definitions**, create a COUNT definition `Households reached` (population, criteria, method, unit `households`) and submit it for review. As `reviewer` approve it in **Review queue**.
3. As `author` open **Indicators**, place the approved definition in the programme with `Author` as collector and `Reviewer` as independent reviewer.
4. Open **Collection plans**, choose the indicator and 2026-Q3, add two obligations (source keys `UAT-D01-2026Q3`, `UAT-D02-2026Q3`), submit; as `reviewer` approve.
5. As `author` activate the indicator, then in **Portfolio** choose **Mark ready** and **Activate programme**.

6. Repeat steps 1–5 for a second programme `UAT Field Collection` with a COUNT definition `Households visited` (unit `households`) and one obligation. Scenarios 8 and 9 use this programme; its period is never closed in this pack.

Expected: each approval freezes an immutable revision; editing an approved definition creates a new draft revision rather than changing the approved one; the programme cannot become Ready while a readiness check fails.

Why two programmes: a period close refuses while any observation of the programme's indicators in that period is not one of the planned sources (`UNPLANNED_VALUES`), and this build cannot plan import sources in advance (their source key contains the batch identifier). Imported rows in `UAT Water Access` would therefore block scenario 13.

Result: [ ] Pass [ ] Fail — notes:

### Scenario 7 — Results framework and targets (Track L)

Requirements: FR-PLN-001, FR-PLN-003, FR-PLN-010, FR-IND-003, FR-ANA-003. BRD: UAT05 (part: original target kept, revised target reviewed).

1. As `author` open **Results framework**, choose `UAT Water Access`, and on **Framework** add an impact, an outcome and an output node with owners; place `Households reached` on the output.
2. Try to make a node its own ancestor (a cycle). Then read the **Completeness review**; document an exception for one warning with a reason and a future review date.
3. Submit; as `reviewer` approve it in **Review queue**.
4. On **Targets** create a VALUE target of 100 households for 2026-Q3 (direction higher is better) and a baseline; submit; as `reviewer` approve.
5. Create a REVISED target of 80 that names the approved one, with a reason; submit and approve.
6. Open **Targets vs actuals**.

Expected: step 2's cycle is refused and cannot be excepted; the exception records who documented it and when; step 3 freezes baseline 1 including the exception; step 5 keeps the original target on record beside the revision; step 6 shows the target, baseline and the actual marked provisional until the period is closed. A blank target is recorded as missing, never zero.

Result: [ ] Pass [ ] Fail — notes:

### Scenario 8 — Web form: design, review, publish, submit (Track L)

Requirements: FR-FRM-001, FR-FRM-002, FR-FRM-003, FR-FRM-006. BRD: none completely (UAT21/22 are offline and out of Release 1).

1. As `author` open **Forms**, choose `UAT Field Collection`, **New form** `UAT household visit`, with questions: `district` (text, required), `visited` (yes/no, required), `households` (whole number, required, minimum 0, **Ask only when** `visited` = yes, **Feeds indicator** `Households visited` as the value).
2. **Save draft**, **Send for review**; as `reviewer` approve in **Review queue**; as `author` **Publish** (sign in again if more than five minutes have passed).
3. **Fill in** with reporting unit `UAT-F01`, `visited` = yes, `households` = 12; **Save draft**, reopen, **Submit response**.
4. Fill in a second response with `visited` = no and submit.
5. Submit the first response again from the same dialog (simulating a dropped connection).
6. Start a response, then publish a **New version** of the form, then submit the old response.

Expected: step 3 creates one observation of 12 in the ordinary review queue; step 4 records `households` as not applicable (never zero); step 5 returns the original receipt, not a second response; step 6 keeps the response unchanged as Quarantined with no observation. The person who filled in a response cannot approve its observation.

Result: [ ] Pass [ ] Fail — notes:

### Scenario 9 — CSV import with quarantine and duplicates (Track L)

Requirements: FR-DAT-001, FR-DAT-002, FR-DAT-004, FR-DQ-003, FR-DQ-007. BRD: UAT23 (part: dates are never reinterpreted; repeated records are caught).

Save these two files exactly (UTF-8, comma-separated, first row is the header). All values are invented.

`uat-import-clean.csv`:

```
district,households,remarks
UAT-D11,12,first
UAT-D12,,blank is missing
UAT-D13,NA,declared not applicable
UAT-D14,0,zero is a value
00123UAT,7,"quoted, comma"
```

`uat-import-problems.csv`:

```
district,households,date
UAT-D11,9,2026-08-01T00:00:00Z
UAT-D21,4,2026-08-02T00:00:00Z
UAT-D21,6,2026-08-03T00:00:00Z
UAT-D22,abc,2026-08-04T00:00:00Z
UAT-D23,2.5,2026-08-05T00:00:00Z
UAT-D24,-3,2026-08-06T00:00:00Z
UAT-D25,3,2025-01-01T00:00:00Z
UAT-D26,3,03/04/2026
,3,2026-08-07T00:00:00Z
UAT-D27,3
UAT-D28,1001,2026-08-08T00:00:00Z
UAT-D29,8,2026-08-09T00:00:00Z
```

1. As `author` open **Imports**, **New batch**: programme `UAT Field Collection`, period 2026-Q3, file `uat-import-clean.csv`, unit column `district`, value column `households` mapped to `Households visited` (role value, unit `households`, minimum 0, maximum 1000), missing-value token `NA` = not applicable, mode partial. Save and preview.
2. Commit. Then as `author` try to approve one of the imported observations in **Review queue**; as `reviewer` approve them.
3. **New batch** with `uat-import-problems.csv`, the same mapping plus event-date column `date`, mode **atomic**. Preview, then try to commit.
4. Change the batch to partial mode, preview again and commit.
5. Rename the header `households` to `hh` in a copy of the file and preview it with the same mapping.

Expected: step 1 shows 5 rows, all accepted, `remarks` listed as dropped, the blank as missing, `NA` as not applicable, `0` as the value zero, `00123UAT` and the quoted comma kept exactly; preview writes no observation. Step 2: the batch author cannot approve (independence). Step 3: 12 rows reconcile as 2 accepted, 8 quarantined, 2 duplicate — `UAT-D11` duplicate of the earlier batch (`DUPLICATE_UNIT_PERIOD`), the second `UAT-D21` (`DUPLICATE_IN_BATCH`), `abc` (`VALUE_NOT_NUMERIC`), `2.5` (`VALUE_TYPE_INVALID`), `-3` and `1001` (`VALUE_OUT_OF_RANGE`), the 2025 date (`EVENT_OUTSIDE_PERIOD`), `03/04/2026` (`EVENT_AT_INVALID`: no date pattern was declared, so it is not guessed), the empty district (`UNIT_KEY_MISSING`), the short row (`ROW_SHAPE_INVALID`); the atomic commit is refused and commits nothing. Step 4 commits exactly the 2 accepted rows and keeps the rest on the batch. Step 5 is refused before any row is read (`MAPPING_COLUMN_MISSING`); values are never shifted into another column. Note for the record: the imported observations are unplanned sources of `UAT Field Collection`, so its 2026-Q3 period cannot be closed (`UNPLANNED_VALUES`) until a reviewed collection-plan change names their exact keys; since build 0.27.0 that clears the blocker (verified in `qualification/test_import.py::test_unplanned_import_units_still_block_close`), and planning the `IMPORT/<unit>/<indicator>/<period>` keys before importing avoids it.

Result: [ ] Pass [ ] Fail — notes:

### Scenario 10 — Evidence upload and mediated download (Track L)

Requirements: FR-EVD-001, FR-SEC-005. BRD: none directly.

1. As `author` open an observation from scenario 6 or 8. In its **Evidence** section choose a small synthetic PDF or PNG you made for the test (no real document), type `Attendance sheet`, a source and a date; upload and attach.
2. Download it from the same section.
3. Upload a second version of the evidence, then reopen the observation.
4. Try to upload a file named `report.pdf.exe`, and a PNG declared as PDF. With the engineer, upload the standard EICAR anti-virus test file (the engineer supplies it).
5. Sign in as `partner` and try the download address from step 2.

Expected: step 1 hashes the file in the browser, waits for the verdict and attaches it; step 2 downloads the exact file as an attachment; step 3: the observation still cites version 1 and notes that a newer version exists; step 4: both names are refused before any byte is sent and the EICAR file is marked infected and is never downloadable; step 5: not available unless `partner` holds evidence download. The screen states that the scan is not malware protection — it is not.

Result: [ ] Pass [ ] Fail — notes:

### Scenario 11 — Review independence (Track L)

Requirements: FR-WFL-002, FR-WFL-003, FR-ACC-004. BRD: UAT12.

1. As `author` add an observation in **Measurement** (source key unique to you, event date 2026-08-15, value 80, numerator 8, denominator 10 for the seeded indicator) and **Submit for review**.
2. In **Review queue** try to approve it as `author`.
3. As `reviewer` open it, **return** it with a comment; as `author` correct it and resubmit; as `reviewer` approve.
4. As `reviewer`, edit a candidate before approving it, then try to approve.

Expected: step 2 is refused for independence even though `author` holds the reviewer role; step 3 approves only the exact revision the reviewer saw; step 4: editing as a reviewer makes you an author, so your own approval is refused.

Result: [ ] Pass [ ] Fail — notes:

### Scenario 12 — Calculation (Track L)

Requirements: FR-CAL-001, FR-CAL-003, FR-CAL-008, FR-CAL-009, FR-CAL-010, FR-CAL-011, VF-DIN-001. BRD: UAT01, UAT04 (part), UAT09 (part).

1. After scenario 11, open **Results** and **Calculate result** for the seeded indicator and 2026-Q3.
2. Open the result and read the contributions, exclusions and coverage.
3. Add and approve another observation in the period, then refresh **Results**.
4. For `Households reached`, capture and approve one manual observation for each planned obligation of scenario 6 (in **Measurement**, using exactly the planned source keys), then calculate.

Expected: on a fresh fixture step 1 shows **49.17** from pooled components **59 / 120**, marked **PROVISIONAL** (the seeded 50/100 and 1/10 plus your 8/10; never the average of the displayed percentages); step 3 marks the earlier result stale and keeps it unchanged; step 4 counts only approved values of the planned sources — a missing or not-applicable value is never treated as zero, and a zero denominator in a ratio is shown as undefined, never 0.

Result: [ ] Pass [ ] Fail — notes:

### Scenario 13 — Period close and restatement (Track L)

Requirements: FR-WFL-007, FR-WFL-008, FR-DQ-006. BRD: UAT05 (part), UAT07 (part).

1. Make sure every obligation of `UAT Water Access` for 2026-Q3 is approved (scenario 12 step 4), that no unplanned observation of its indicators exists in the period, and calculate a current result.
2. As `author` open **Period close**, choose the programme and 2026-Q3, **Preview period close**, read blockers, give a reason and submit.
3. Before approval, change a source (approve a new observation); as `reviewer` try to approve the close.
4. Preview again and approve as `reviewer`.
5. Try to submit a new observation in the locked period.
6. **Request restatement** for one named source with a window of at most seven days; approve as `reviewer`; correct, recalculate and close again.

Expected: step 3 is refused because the sources changed since preview; step 4 creates OFFICIAL results and a locked snapshot, pinning the approved targets and the governing framework revision; step 5 is refused; step 6 creates a new snapshot that supersedes, not overwrites, the first.

Result: [ ] Pass [ ] Fail — notes:

### Scenario 14 — Dashboard (Track L)

Requirements: FR-ANA-003, FR-ANA-004. BRD: none completely.

1. As `author` open **Dashboards**, choose `UAT Water Access` and 2026-Q3.
2. Repeat with a period that has no locked snapshot.

Expected: step 1 shows the OFFICIAL value from this programme's locked snapshot and, separately, any newer PROVISIONAL value; target, baseline, status against target, coverage and freshness, with the stale rule written out; the trend chart has an equivalent table. Step 2 states "no locked snapshot — values are provisional". A period with no required obligation shows coverage as not applicable, never 100 %. The seeded OFFICIAL 46.36 appears nowhere (it belongs to no programme).

Result: [ ] Pass [ ] Fail — notes:

### Scenario 15 — Report package (Track L)

Requirements: FR-RPT-003, FR-RPT-004, FR-RPT-010. BRD: UAT07 (part: the original report stays frozen).

1. As `author` open **Reports**, choose the approved template, the locked snapshot from scenario 13 and an official snapshot result; in the narrative write `Households reached: {{total_reached}}` with that placeholder bound to the result; also try a sentence with a bare number such as `We reached 120 households.`
2. Save, **Submit for review**; as `reviewer` approve.
3. **Open approved export** and **Download CSV**.
4. Restate and close the period again (scenario 13 step 6), then reopen the report.

Expected: step 1's bare numeric claim is refused; step 3 shows the frozen values exactly as stored; step 4: the approved report keeps its original numbers.

Result: [ ] Pass [ ] Fail — notes:

### Scenario 16 — PDF, XLSX and DOCX export (Track L)

Requirements: FR-RPT-005, FR-RPT-003. BRD: none directly.

1. On the approved report's detail, under **Rendered exports**, request PDF, XLSX and DOCX.
2. Wait for each to show Succeeded (the worker renders them), then download each.
3. Request the same format again. If any export is still Queued, choose **Cancel** on it.

Expected: every number in the three files is the same displayed value as the HTML and CSV of scenario 15; the XLSX stores values as text (no formulas, no re-rounding); step 3: a second identical request is refused; a queued export is cancelled before it starts, while one the worker has already started is not cancelled. Note for the record: the PDF is not tagged for accessibility and has no charts.

Result: [ ] Pass [ ] Fail — notes:

### Scenario 17 — Controlled publication and withdrawal (Track L)

Requirements: FR-RPT-007, FR-RPT-009. BRD: UAT13 (part), UAT07 (part).

1. As `author` on the approved report choose **Request controlled publication**: recipient `partner`, a purpose, an expiry within 90 days, download allowed, and include the PDF from scenario 16.
2. Try to approve it as `author`; approve it as `reviewer` in **Review queue**; publish it from **Reports**.
3. As `partner` open the publication and download the CSV and the PDF.
4. As `other_tenant` and as `enumerator` try the same addresses.
5. As the publisher withdraw it with a reason; as `partner` try again.

Expected: step 2's self-approval is refused; the reviewer approves the exact bytes; step 3 works and each download is logged; step 4 answers "not available"; step 5 makes it unavailable to `partner` while the frozen artifacts and access log remain. Bytes already downloaded are not recalled.

Result: [ ] Pass [ ] Fail — notes:

### Scenario 18 — Data-subject request (Track L)

Requirements: FR-PRV-005, FR-PRV-007, VF-PRV-001. BRD: UAT15 is **not** covered (deletion replay after a restore does not exist).

1. As `admin` open **People & access → Data-subject requests**, record an ACCESS request for `partner` with a reason and verification note.
2. As `privacy` review the plan, **Approve this plan**, execute, and download the export package.
3. Record an ERASURE request for the member you invited in scenario 5 after revoking that membership; as `privacy` approve and execute.
4. As `privacy`, record a request and try to approve it yourself; then try to approve an erasure for a member who is still active.
5. Check scenario 13's official results after step 3.

Expected: step 2's package covers the subject's own data only (no other person's details) and expires after 7 days; step 3 replaces the member's display name with "Erased member" and removes their invitation details, sealed addresses and named files; step 4 is refused (independence; `SUBJECT_STILL_ACTIVE`); step 5: official numbers are unchanged. On Track S this scenario cannot be performed (no purpose-bound grant can be issued).

Result: [ ] Pass [ ] Fail — notes:

### Scenario 19 — Audit export (Track L)

Requirements: VF-AUD-001, FR-SEC-007. BRD: none directly.

1. As `admin` open **People & access → Audit export**, choose a window that has ended (for example yesterday), purpose `INTERNAL_AUDIT`, a reason, and export.
2. Download the `.jsonl` page and the manifest; open the next page if there is one.
3. Try a window that ends in the future.

Expected: step 1 shows the page summary with its digest, chain end and seal key; the export itself appears as an audit event; no payload, address or secret appears in the file; step 3 is refused. Denied attempts are not themselves audited in this build.

Result: [ ] Pass [ ] Fail — notes:

### Scenario 20 — Health, account support and the restore drill (Track S, owner)

Requirements: FR-OPS-005, FR-OPS-006, VF-OBS-001, VF-DR-003. BRD: UAT19 is **not** covered (single server).

1. Open https://168-144-78-191.sslip.io/deploy-status.json.
2. In the droplet console: `sudo /opt/impact/repo/deploy/list-users.sh`, then `sudo /opt/impact/repo/deploy/reset-user.sh <a tester's e-mail>`; the tester signs in with the new one-time password.
3. `sudo /opt/impact/repo/deploy/restore-drill.sh`, then reload the status page.

Expected: step 1 shows `"result": "ok"`, the deployed commit, `"alerts": []`, and under `operations` the newest backup and its age and the last drill; no password or secret appears anywhere. Step 2 prints the password once in a box and the tester must set a new one. Step 3 prints PASS with its duration, and `operations.restore_drill` shows the new result. Follow the [support runbook](SUPPORT-RUNBOOK.md) for any alert.

Result: [ ] Pass [ ] Fail — notes:

### Scenario 21 — Failed deliveries and the operator re-queue (Track S or L)

Requirements: FR-TEN-001 (delivery part), VF-OBS-001. BRD: none directly.

1. As a platform operator open **Tenant lifecycle → Workers**: read the worker heartbeat and **Deliveries needing attention**.
2. If a row is listed as DEAD (Track L: the engineer produces one with the synthetic sink's failure setting), choose **Re-queue** with a reason.

Expected: rows show state, attempts and error class but never an address, link or code; re-queue needs a fresh sign-in and a reason, and the worker then delivers or supersedes the row (an invitation that was reissued is never sent). Nothing is replayed automatically.

Result: [ ] Pass [ ] Fail — notes:

### Scenario 22 — Keyboard-only pass (Track L)

Requirements: FR-UX-004, VF-UX-001. BRD: UAT30 (part: keyboard only; no screen-reader review).

1. Without a mouse, sign in, move through the main navigation, open a record, submit an observation for review and, as `reviewer`, approve it.

Expected: every control is reachable with Tab, focus is always visible, dialogs keep focus inside and return it on close, errors are announced in text. Record any trap or invisible focus with the screen and step.

Result: [ ] Pass [ ] Fail — notes:

## 5. Not in Release 1 yet — do not test, record as excluded

- On staging: reporting calendars, periods, review templates and report templates for a new tenant; the newer capabilities in the onboarding access package; a second platform operator; purpose-bound privacy grants (see section 1).
- E-mail to real mailboxes (no provider: invitations and codes are captured on the server), "Forgot password", identity recovery beyond the console reset, MFA recovery, sign-in key rotation.
- Off-server backups, a recovery-time or recovery-point objective, deletion replay after a restore (UAT15), regional recovery (UAT19), alert paging.
- Forms: repeat groups, translations, photos and locations, rounds and assignments, correcting a returned response, offline and Android collection (UAT21, UAT22).
- Imports: reusable reviewed mappings, keyed update or replacement, quality issues and exceptions, reconciliation, schema-drift review across recurring loads.
- Evidence: a real malware scanner, verification and dispute, search, redaction, multipart uploads.
- Reports and dashboards: charts in reports, tagged PDF, non-Latin PDF fonts, scheduled distribution, dashboard authoring, filters and drill-down, dashboard export.
- Calculation: overlap and unique reach (UAT02), cumulative semantics (UAT03), hierarchy (UAT06), crosswalks and conversions (UAT08), status thresholds, disaggregated targets.
- Privacy: participants as data subjects, retention-hold management, tenant retention policies, encryption at rest under a platform key.
- Support access (UAT17), entitlements (UAT18), tenant exit (UAT20), AI (UAT24–UAT29), evaluation, finance, integrations, migration tooling.

## 6. Sign-off sheet

| Scenario | Track | Tester | Date (UTC) | Commit | Pass / Fail | Defect or correlation ID |
|---|---|---|---|---|---|---|
| 1 | S | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |
| 6 | L | | | | | |
| 7 | L | | | | | |
| 8 | L | | | | | |
| 9 | L | | | | | |
| 10 | L | | | | | |
| 11 | L | | | | | |
| 12 | L | | | | | |
| 13 | L | | | | | |
| 14 | L | | | | | |
| 15 | L | | | | | |
| 16 | L | | | | | |
| 17 | L | | | | | |
| 18 | L | | | | | |
| 19 | L | | | | | |
| 20 | S | | | | | |
| 21 | | | | | | |
| 22 | L | | | | | |

Programme owner: ____________________ Date: __________ Independent control reviewer: ____________________ Date: __________

Signing this sheet records what was observed. It is not the release decision, which follows the [release acceptance procedure](RELEASE-ACCEPTANCE.md) once the gaps in [RELEASE-1-ACCEPTANCE-GAPS.md](RELEASE-1-ACCEPTANCE-GAPS.md) are closed or explicitly excluded by a recorded scope decision.
