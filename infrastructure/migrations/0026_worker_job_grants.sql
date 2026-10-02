BEGIN;
SET LOCAL ROLE impact_owner;
-- Worker privileges, part 2 (integration of builds 0.21.0-0.24.0, October 2026).
-- Migration 0025 left four tables of migration 0003's SELECT/INSERT/UPDATE grant to impact_worker
-- untouched until report exports (0024) had settled the worker's job privileges. 0024 grants the
-- worker exactly what the REPORT_EXPORT job class and the cancellation pass use (worker.py):
--   job        SELECT, UPDATE  (claim, lease renewal, fenced outcome, cancellation before start)
--   job_item   SELECT, INSERT  (artifact and cancellation outcomes; never updated)
-- The worker never inserts a job (jobs are requested by the application) and never reads or writes
-- report_current or report_template_current (an export reads the pinned package through
-- object_revision and report_package_binding). Those privileges are revoked here; a REVOKE removes
-- only what it names, so the grants of 0024 that the worker uses stay in place. impact_app is not
-- touched.
REVOKE INSERT ON impact.job FROM impact_worker;
REVOKE UPDATE ON impact.job_item FROM impact_worker;
REVOKE ALL ON impact.report_current FROM impact_worker;
REVOKE ALL ON impact.report_template_current FROM impact_worker;
COMMIT;
