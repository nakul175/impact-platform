# Sunday backup qualification correction

Proposed maintenance change on build 0.28.0 (schema 33). No runtime backup change, migration, API route, version bump or requirement-status change.

The four PR checks for #82 passed on 3 October. After #82 merged as `6712970` on Sunday 4 October, the `main` PGlite job failed `test_backup_set_holds_databases_roles_objects_and_a_verified_manifest`: the backup script correctly kept the day's weekly hard-linked set, while that test asserted the weekly list was empty. `test_sundays_set_is_kept_weekly_by_hard_link_and_retention_prunes_oldest` already pins Sunday and verifies the weekly set.

The ordinary daily test now pins Monday through its existing `WEEKDAY` stub. It still checks the manifest, hashes, objects, permissions and status, and the Sunday test still checks retention and hard links. Both focused tests and the full `qualification/test_ops_unit.py` file pass locally (41 tests). CI must rerun the full suite. The staging server remains unverified from this workspace; this test correction does not establish its health.
