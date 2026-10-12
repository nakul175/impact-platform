import json
import logging
import re
from time import monotonic
from urllib.parse import parse_qs, quote, urlparse
from uuid import UUID, uuid4
import psycopg
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, Response
from fastapi.exceptions import RequestValidationError
from starlette.concurrency import run_in_threadpool
from starlette.staticfiles import StaticFiles
from .config import Settings, ROOT
from .auth import Auth
from .account import Account
from .domain import DomainError
from .service import Service
from .administration import Administration
from .administration_contracts import COMMANDS, ADMIN_READS
from .reporting import REPORT_CSP
from .content_safety import MAX_EVIDENCE_BYTES
from .store import Database
from .tenant_lifecycle import TenantLifecycle
from .access_bootstrap import AccessBootstrap
from .authority_renewal import AuthorityRenewal
from .access_upgrade import AccessUpgrade
from .recovery_contacts import RecoveryContacts
from .worker_status import WorkerStatus
from .delivery_operations import DeliveryOperations
from .operators import Operators
from .ops_metrics import OpsMetrics, RequestMetrics
from .status import Status
from .version import BUILD, DOMAIN_API, SCHEMA
from .audit_export import AuditExports
from .retention_policies import RetentionPolicies
from . import security_events
from .dashboards import Dashboards
from .logframe import LogframeExports, MEDIA as LOGFRAME_MEDIA
from .ai_enablement import AIEnablement
from .ai_jobs import AIJobs
from .ai_forecasts import AIForecasts
from .ai_safety import AISafety
from .ai_extraction import AIExtraction
from .ai_indicator_design import AIIndicatorDesign
from .ai_policy import AIPolicy
from .ai_ranking import AIRanking
from .ai_adoption_plans import AIAdoptionPlans
from .ai_role_training import AIRoleTraining
from .ai_champion_appointments import AIChampionAppointments
from .ai_diagnoses import AIDiagnoses
from .ai_diagnosis_contributions import AIDiagnosisContributions
from .ai_diagnosis_reviews import AIDiagnosisReviews
from .ai_solution_fit_scores import AISolutionFitScores
from .ai_problem_baselines import AIProblemBaselines
from .ai_outcome_observations import AIOutcomeObservations
from .ai_sponsor_value_reports import AISponsorValueReports
from .ai_quarterly_value_reviews import AIQuarterlyValueReviews
from .ai_outcome_evidence import AIOutcomeEvidence
from .ai_next_opportunities import AINextOpportunities
from .ai_value_case_versions import AIValueCaseVersions
from .ai_opportunity_mapping import AIOpportunityMapping
from .ai_plan_exports import AIPlanExports
from .ai_impact_references import AIImpactReferences
from .human_advice import HumanAdviceCases
from .sponsored_access import SponsoredAccess
from .entitlement_view import EntitlementView
from .service_packages import ServicePackages
from .tax_invoicing import TaxInvoicing
from .agreement_coverage import AgreementCoverage
from .access_checks import AccessChecks
from .fine_grained_access import FineGrainedAccess
from .effective_access import EffectiveAccess
from .permission_safe_derivatives import PermissionSafeDerivatives
from .external_shares import ExternalShares
from .access_change_propagation import AccessChangePropagation
from .ai_trials import AITrials
from .partner_revenue import PartnerRevenue
from .human_advice_contracts import ACTION_DATA as HUMAN_ADVICE_ACTIONS
from .ai_advisory_provider import OpenAIAdvisory
from .contracts import validate

LOG = logging.getLogger("impact")
MAX_BODY = 262144
# The one route whose body is raw bytes rather than JSON: an evidence upload's whole content, at most
# the design ceiling for EVIDENCE_MEDIA and never more than the upload's own declared size.
# admin_shutdown, crash_shutdown, cannot_connect_now: the server is going or not yet back.
DATABASE_SHUTDOWN = {"57P01", "57P02", "57P03"}
UPLOAD_CONTENT = re.compile(r"^/v1/tenants/[^/]+/uploads/[^/]+/content$")
# A logout token is at most 16 KiB (Auth.backchannel_logout); the form adds "logout_token=".
MAX_LOGOUT_BODY = 16384 + 64


async def bounded_body(request, limit):
    """The request body read chunk by chunk and refused once it exceeds `limit`: the middleware's
    Content-Length check does not bound a chunked body."""
    raw = bytearray()
    async for chunk in request.stream():
        raw.extend(chunk)
        if len(raw) > limit:
            raise DomainError("LIMIT_EXCEEDED", 413)
    return bytes(raw)


async def strict_body(request):
    if request.headers.get("content-type", "").split(";")[0] != "application/json":
        raise DomainError("VALIDATION_FAILED", 415)
    raw = await bounded_body(request, MAX_BODY)

    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                raise ValueError
            result[k] = v
        return result

    def constant(_):
        raise ValueError

    try:
        data = json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
        json.dumps(data, ensure_ascii=False).encode("utf-8")
        if not isinstance(data, dict):
            raise ValueError
        return data
    except (ValueError, UnicodeError):
        raise DomainError("VALIDATION_FAILED", 400) from None


def uuid(value):
    try:
        return str(UUID(value))
    except ValueError:
        raise DomainError("RESOURCE_UNAVAILABLE", 404) from None


def create_app():
    s = Settings.load()
    db = Database(s)
    auth = Auth(s, db)
    account = Account(auth)
    service = Service(s, db)
    ai_enablement = AIEnablement(service, OpenAIAdvisory(s.ai_api_key, s.ai_model), enabled=s.ai_enabled)
    ai_jobs = AIJobs(service, ai_enablement)
    ai_forecasts = AIForecasts(service)
    ai_safety = AISafety(service)
    ai_extraction = AIExtraction(
        service, ai_enablement.provider.destination, ai_enablement.provider.evaluation_configuration
    )
    ai_indicator_design = AIIndicatorDesign(
        service, ai_enablement.provider.destination, ai_enablement.provider.evaluation_configuration
    )
    ai_policy = AIPolicy(service, ai_enablement.server_ready)
    ai_plans = AIAdoptionPlans(service)
    ai_role_training = AIRoleTraining(service)
    ai_champion_appointments = AIChampionAppointments(service)
    ai_diagnoses = AIDiagnoses(service)
    ai_diagnosis_contributions = AIDiagnosisContributions(service, ai_diagnoses)
    ai_diagnosis_reviews = AIDiagnosisReviews(service, ai_diagnoses)
    ai_solution_fit_scores = AISolutionFitScores(service)
    ai_problem_baselines = AIProblemBaselines(service, ai_diagnoses)
    ai_outcome_observations = AIOutcomeObservations(service, ai_diagnoses, ai_problem_baselines)
    ai_sponsor_value_reports = AISponsorValueReports(service, ai_outcome_observations)
    ai_quarterly_value_reviews = AIQuarterlyValueReviews(service, ai_outcome_observations)
    ai_next_opportunities = AINextOpportunities(service, ai_diagnoses)
    ai_value_cases = AIValueCaseVersions(service)
    ai_opportunity_mapping = AIOpportunityMapping(ai_diagnoses)
    ai_ranking = AIRanking(service, mappings=ai_opportunity_mapping)
    ai_plan_exports = AIPlanExports(service)
    human_advice = HumanAdviceCases(service)
    sponsored_access = SponsoredAccess(service)
    entitlement_view = EntitlementView(service)
    service_packages = ServicePackages(service)
    tax_invoicing = TaxInvoicing(service)
    agreement_coverage = AgreementCoverage(service)
    access_checks = AccessChecks(service)
    fine_grained_access = FineGrainedAccess(service)
    effective_access = EffectiveAccess(service)
    permission_safe_derivatives = PermissionSafeDerivatives(service)
    external_shares = ExternalShares(service, permission_safe_derivatives)
    access_change_propagation = AccessChangePropagation(service, permission_safe_derivatives)
    ai_trials = AITrials(service, ai_value_cases)
    administration = Administration(s, db, service)
    lifecycle = TenantLifecycle(s, db)
    partner_revenue = PartnerRevenue(lifecycle)
    ai_outcome_evidence = AIOutcomeEvidence(service, lifecycle)
    bootstrap_access = AccessBootstrap(lifecycle)
    authority_renewal = AuthorityRenewal(lifecycle)
    access_upgrade = AccessUpgrade(lifecycle)
    recovery_contacts = RecoveryContacts(lifecycle)
    worker_status = WorkerStatus(lifecycle)
    dashboards = Dashboards(service)
    ai_impact = AIImpactReferences(service, dashboards)
    audit_exports = AuditExports(service)
    retention_policies = RetentionPolicies(service)
    delivery_operations = DeliveryOperations(lifecycle)
    operators = Operators(lifecycle)
    request_metrics = RequestMetrics()
    ops_metrics = OpsMetrics(lifecycle, request_metrics)
    status = Status(lifecycle)
    app = FastAPI(title="Impact Platform", version=BUILD, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.services = (s, db, auth, service)

    def error(request, exc):
        return JSONResponse(
            {
                "code": exc.code,
                "message": exc.message,
                "retryable": exc.status == 503,
                "correlation_id": getattr(request.state, "correlation", str(uuid4())),
                "permitted_actions": [],
                "field_errors": exc.fields,
                **({"reason_code": exc.reason} if exc.reason else {}),
            },
            status_code=exc.status,
        )

    @app.exception_handler(DomainError)
    async def domain_error(request, exc):
        # Denial auditing (v0.27): a refused authorisation is recorded in its own transaction after
        # the refused one rolled back; recording never changes the response.
        if getattr(exc, "denial", None):
            await run_in_threadpool(
                security_events.record, db, exc.denial, request.state.correlation, request.url.path
            )
        if getattr(exc, "calculation_failure", None):
            try:
                await run_in_threadpool(service.record_calculation_failure, exc.calculation_failure)
            except Exception:
                LOG.exception("Could not preserve calculation failure receipt")
        return error(request, exc)

    @app.exception_handler(RequestValidationError)
    async def request_error(request, exc):
        return error(request, DomainError("VALIDATION_FAILED"))

    @app.exception_handler(psycopg.Error)
    async def database_error(request, exc):
        LOG.error(
            "database failure correlation=%s sqlstate=%s constraint=%s column=%s message=%s",
            request.state.correlation,
            exc.sqlstate,
            exc.diag.constraint_name,
            exc.diag.column_name,
            exc.diag.message_primary,
        )
        if exc.sqlstate in {"40001", "40P01", "55P03"}:
            return error(request, DomainError("CONFLICT_VERSION", 409))
        if (exc.sqlstate or "").startswith("23"):
            return error(request, DomainError("VALIDATION_FAILED"))
        # A refused, lost or shut-down database connection (no SQLSTATE, class 08 or an operator
        # shutdown) is named for the caller and readiness; the transaction it carried never committed.
        if isinstance(exc, psycopg.OperationalError) and (
            not exc.sqlstate or exc.sqlstate.startswith("08") or exc.sqlstate in DATABASE_SHUTDOWN
        ):
            return error(request, DomainError("SERVICE_UNAVAILABLE", 503, reason="DATABASE_UNAVAILABLE"))
        return error(request, DomainError("SERVICE_UNAVAILABLE", 503))

    @app.exception_handler(Exception)
    async def unexpected(request, exc):
        LOG.error(
            "unexpected failure correlation=%s type=%s",
            getattr(request.state, "correlation", "none"),
            type(exc).__name__,
        )
        return error(request, DomainError("SERVICE_UNAVAILABLE", 503))

    @app.middleware("http")
    async def security(request, call_next):
        started = monotonic()
        supplied = request.headers.get("x-correlation-id", "")
        try:
            request.state.correlation = str(UUID(supplied))
        except ValueError:
            request.state.correlation = str(uuid4())
        host = request.headers.get("host", "").split(":")[0]
        limit = (
            MAX_EVIDENCE_BYTES
            if request.method == "PUT" and UPLOAD_CONTENT.fullmatch(request.url.path)
            else MAX_BODY
        )
        if host not in {urlparse(s.public_origin).hostname, "testserver" if s.environment == "test" else ""}:
            response = error(request, DomainError("VALIDATION_FAILED", 400))
        elif (
            request.headers.get("content-length", "0").isdigit()
            and int(request.headers.get("content-length", "0")) > limit
        ):
            response = error(request, DomainError("LIMIT_EXCEEDED", 413))
        else:
            response = await call_next(request)
        response.headers.update(
            {
                "X-Correlation-ID": request.state.correlation,
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "no-referrer",
                "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
            }
        )
        if "Content-Security-Policy" not in response.headers:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
                "connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; "
                "form-action 'self'"
            )
        if s.secure:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        request_metrics.observe(request.url.path, response.status_code, monotonic() - started)
        return response

    @app.get("/health/live")
    def live():
        return {"status": "live"}

    @app.get("/health/ready")
    def ready():
        # With unprivileged connections required, readiness first proves the app, identity and
        # platform connections are three distinct non-privileged logins (see Database.verify_topology).
        db.verify_topology()
        with db.transaction() as c:
            version = c.execute("SELECT max(version) AS version FROM impact.schema_migration").fetchone()[
                "version"
            ]
        if version != SCHEMA:
            raise DomainError("SERVICE_UNAVAILABLE", 503)
        return {"status": "ready"}

    @app.get("/auth/mode")
    def mode():
        return {"development": s.dev_auth}

    @app.get("/v1/platform/tenants")
    def tenant_directory(request: Request, cursor: str | None = None):
        return lifecycle.directory(auth.resolve(request), uuid(cursor) if cursor else None)

    @app.get("/v1/platform/recovery-contacts")
    def recovery_directory(request: Request, cursor: str | None = None):
        return recovery_contacts.directory(auth.resolve(request), uuid(cursor) if cursor else None)

    @app.post("/v1/platform/tenants/{tenant_id}/recovery-contacts")
    async def nominate_recovery_contact(request: Request, tenant_id: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            recovery_contacts.command, auth.resolve(request), "nominate", body, uuid(tenant_id)
        )

    @app.post("/v1/platform/recovery-contacts/{contact_id}/actions/{action}")
    async def recovery_action(request: Request, contact_id: str, action: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            recovery_contacts.command, auth.resolve(request), action, body, None, uuid(contact_id)
        )

    @app.get("/v1/platform/workers")
    def worker_directory(request: Request):
        return worker_status.directory(auth.resolve(request))

    @app.get("/v1/platform/metrics")
    def platform_metrics(request: Request):
        return ops_metrics.summary(auth.resolve(request))

    @app.get("/v1/platform/deliveries")
    def delivery_attention(request: Request, tenant_id: str | None = None):
        return delivery_operations.directory(auth.resolve(request), uuid(tenant_id) if tenant_id else None)

    @app.post("/v1/platform/tenants/{tenant_id}/deliveries/{event_id}/actions/{action}")
    async def delivery_action(request: Request, tenant_id: str, event_id: str, action: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            delivery_operations.command, auth.resolve(request), action, body, uuid(tenant_id), uuid(event_id)
        )

    @app.get("/v1/platform/access-bootstraps")
    def initial_access_directory(request: Request, cursor: str | None = None):
        return bootstrap_access.directory(auth.resolve(request), uuid(cursor) if cursor else None)

    @app.post("/v1/platform/tenants/{tenant_id}/access-bootstrap")
    async def request_initial_access(request: Request, tenant_id: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            bootstrap_access.command, auth.resolve(request), "request", body, uuid(tenant_id)
        )

    @app.post("/v1/platform/access-bootstraps/{request_id}/actions/{action}")
    async def initial_access_action(request: Request, request_id: str, action: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            bootstrap_access.command, auth.resolve(request), action, body, None, uuid(request_id)
        )

    @app.get("/v1/platform/access-upgrades")
    def access_upgrade_directory(request: Request, cursor: str | None = None):
        return access_upgrade.directory(auth.resolve(request), after=cursor)

    @app.get("/v1/platform/tenants/{tenant_id}/access-upgrades")
    def tenant_access_upgrades(request: Request, tenant_id: str, cursor: str | None = None):
        return access_upgrade.directory(auth.resolve(request), uuid(tenant_id), cursor)

    @app.get("/v1/platform/tenants/{tenant_id}/access-upgrade-preview")
    def access_upgrade_preview(request: Request, tenant_id: str):
        return access_upgrade.preview(auth.resolve(request), uuid(tenant_id))

    @app.post("/v1/platform/tenants/{tenant_id}/access-upgrade")
    async def request_access_upgrade(request: Request, tenant_id: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            access_upgrade.command, auth.resolve(request), "request", body, uuid(tenant_id)
        )

    @app.post("/v1/platform/tenants/{tenant_id}/access-upgrades/{request_id}/actions/{action}")
    async def access_upgrade_action(request: Request, tenant_id: str, request_id: str, action: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            access_upgrade.command, auth.resolve(request), action, body, uuid(tenant_id), uuid(request_id)
        )

    @app.get("/v1/platform/authority-renewals")
    def authority_renewal_directory(request: Request, cursor: str | None = None):
        return authority_renewal.directory(auth.resolve(request), uuid(cursor) if cursor else None)

    @app.get("/v1/platform/tenants/{tenant_id}/authority")
    def delegated_authority(request: Request, tenant_id: str):
        return authority_renewal.authority(auth.resolve(request), uuid(tenant_id))

    @app.post("/v1/platform/tenants/{tenant_id}/authority-renewal")
    async def request_authority_renewal(request: Request, tenant_id: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            authority_renewal.command, auth.resolve(request), "request", body, uuid(tenant_id)
        )

    @app.post("/v1/platform/authority-renewals/{request_id}/actions/{action}")
    async def authority_renewal_action(request: Request, request_id: str, action: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            authority_renewal.command, auth.resolve(request), action, body, None, uuid(request_id)
        )

    # Operator onboarding and sign-in accounts (v0.26a): identity-authorised control-plane commands.
    @app.get("/v1/platform/operators")
    def operator_directory(request: Request):
        return operators.directory(auth.resolve(request))

    @app.post("/v1/platform/operators/{identity_id}/actions/{action}")
    async def operator_lifecycle_action(request: Request, identity_id: str, action: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            operators.lifecycle_change, auth.resolve(request), action, body, uuid(identity_id)
        )

    @app.post("/v1/platform/operator-nominations")
    async def nominate_operator(request: Request):
        body = await strict_body(request)
        return await run_in_threadpool(operators.nomination, auth.resolve(request), "nominate", body)

    @app.post("/v1/platform/operator-nominations/{nomination_id}/actions/{action}")
    async def operator_nomination_action(request: Request, nomination_id: str, action: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            operators.nomination, auth.resolve(request), action, body, uuid(nomination_id)
        )

    @app.post("/v1/platform/accounts")
    async def create_account(request: Request):
        body = await strict_body(request)
        return await run_in_threadpool(operators.account, auth.resolve(request), "create", body)

    @app.post("/v1/platform/accounts/{account_id}/actions/{action}")
    async def account_action(request: Request, account_id: str, action: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            operators.account, auth.resolve(request), action, body, uuid(account_id)
        )

    @app.post("/v1/platform/partner-revenue-entries", status_code=201)
    async def partner_revenue_entry_create(request: Request):
        body = await strict_body(request)
        return await run_in_threadpool(partner_revenue.entry, auth.resolve(request), body)

    @app.post("/v1/platform/partner-statements", status_code=201)
    async def partner_statement_generate(request: Request):
        body = await strict_body(request)
        return await run_in_threadpool(partner_revenue.statement, auth.resolve(request), body)

    @app.post("/v1/platform/partner-statements/{statement_id}/actions/settle")
    async def partner_statement_settle(request: Request, statement_id: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            partner_revenue.settle, auth.resolve(request), uuid(statement_id), body
        )

    @app.post("/v1/platform/tenants")
    async def request_tenant(request: Request):
        body = await strict_body(request)
        return await run_in_threadpool(lifecycle.command, auth.resolve(request), "request", body)

    @app.post("/v1/platform/tenants/{tenant_id}/actions/{action}")
    async def tenant_action(request: Request, tenant_id: str, action: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            lifecycle.command, auth.resolve(request), action, body, uuid(tenant_id)
        )

    @app.post("/auth/development-login")
    async def development_login(request: Request):
        body = await strict_body(request)
        return await run_in_threadpool(auth.dev_login, request, body)

    @app.get("/auth/login")
    def login():
        return auth.login()

    @app.get("/auth/callback")
    def callback(request: Request):
        return auth.callback(request)

    @app.get("/auth/me")
    def me(request: Request):
        identity = auth.resolve(request)
        return {
            "identity_id": identity.identity_id,
            "csrf_token": auth.csrf(identity.session_id) if identity.session_id else None,
            "tenants": service.tenants(identity)["items"],
            "preferences": account.preferences(identity),
        }

    @app.post("/auth/logout")
    def logout(request: Request):
        return auth.logout(request)

    @app.post("/auth/backchannel-logout")
    async def backchannel_logout(request: Request):
        # Server-to-server from the provider: a form body with exactly one logout_token, no
        # cookie, no Origin; the token signature is the only authentication. Without a live
        # provider the route does not exist, and the body is never read.
        if s.dev_auth or not auth.jwks:
            raise DomainError("RESOURCE_UNAVAILABLE", 404)
        if (
            request.headers.get("content-type", "").split(";")[0].strip()
            != "application/x-www-form-urlencoded"
        ):
            raise DomainError("VALIDATION_FAILED", 400, reason="LOGOUT_TOKEN_INVALID")
        try:
            raw = await bounded_body(request, MAX_LOGOUT_BODY)
            form = parse_qs(raw.decode("ascii"), strict_parsing=True)
        except (UnicodeDecodeError, ValueError):
            raise DomainError("VALIDATION_FAILED", 400, reason="LOGOUT_TOKEN_INVALID") from None
        if set(form) != {"logout_token"} or len(form["logout_token"]) != 1:
            raise DomainError("VALIDATION_FAILED", 400, reason="LOGOUT_TOKEN_INVALID")
        return await run_in_threadpool(auth.backchannel_logout, form["logout_token"][0])

    @app.get("/auth/preferences")
    def preferences(request: Request):
        return account.preferences(auth.resolve(request))

    @app.put("/auth/preferences")
    async def save_preferences(request: Request):
        body = await strict_body(request)
        return await run_in_threadpool(account.save_preferences, auth.resolve(request), body)

    @app.get("/auth/sessions")
    def sessions(request: Request):
        return account.sessions(auth.resolve(request))

    @app.post("/auth/sessions/revoke-all")
    def revoke_all_sessions(request: Request):
        return account.revoke(auth.resolve(request))

    @app.post("/auth/sessions/{session_id}/revoke")
    def revoke_session(request: Request, session_id: str):
        return account.revoke(auth.resolve(request), uuid(session_id))

    @app.get("/v1/status")
    def service_status(request: Request):
        # Every signed-in identity; the closed notice catalogue, plus detail for platform operators.
        return status.read(auth.resolve(request))

    @app.get("/v1/runtime-manifest")
    def manifest(request: Request):
        auth.resolve(request)
        return {
            "environment": s.environment,
            "build_id": "impact-" + BUILD,
            "schema_version": str(SCHEMA),
            "api_version": DOMAIN_API,
            "fixture_id": s.fixture_id,
            "mutation_tests_allowed": s.environment == "test" and bool(s.fixture_id),
        }

    @app.get("/v1/tenants")
    def tenants(request: Request):
        return service.tenants(auth.resolve(request))

    @app.get("/v1/tenants/{tenant}/me/access")
    def access(request: Request, tenant: str):
        return service.access(auth.resolve(request), uuid(tenant))

    @app.get("/v1/tenants/{tenant}/operations/{opid}")
    def receipt(request: Request, tenant: str, opid: str, command_type: str):
        return service.receipt(auth.resolve(request), uuid(tenant), uuid(opid), command_type)

    @app.get("/v1/tenants/{tenant}/programmes/{obj}/readiness")
    def programme_readiness(request: Request, tenant: str, obj: str):
        return service.measurement.read(auth.resolve(request), uuid(tenant), "programme_readiness", uuid(obj))

    @app.get("/v1/tenants/{tenant}/workflows/{obj}/candidate")
    def workflow_candidate(request: Request, tenant: str, obj: str):
        return service.measurement.read(auth.resolve(request), uuid(tenant), "workflow_candidate", uuid(obj))

    @app.get("/v1/tenants/{tenant}/measurement-members")
    def measurement_members(request: Request, tenant: str):
        return service.measurement.read(auth.resolve(request), uuid(tenant), "measurement_members")

    @app.get("/v1/tenants/{tenant}/forms/{obj}/published")
    def form_published(request: Request, tenant: str, obj: str):
        return service.forms.read(auth.resolve(request), uuid(tenant), "get_form_published", uuid(obj))

    @app.get("/v1/tenants/{tenant}/forms/{obj}/completeness")
    def form_completeness(request: Request, tenant: str, obj: str):
        return service.forms.read(auth.resolve(request), uuid(tenant), "get_form_completeness", uuid(obj))

    @app.get("/v1/tenants/{tenant}/collection-rounds/{obj}/coverage")
    def round_coverage(request: Request, tenant: str, obj: str):
        return service.forms.read(auth.resolve(request), uuid(tenant), "get_round_coverage", uuid(obj))

    @app.get("/v1/tenants/{tenant}/ai-enablement/human-advice")
    def human_advice_list(request: Request, tenant: str, limit: int = 50, cursor: str | None = None):
        return human_advice.listing(auth.resolve(request), uuid(tenant), limit, cursor)

    @app.get("/v1/tenants/{tenant}/ai-enablement/human-advice/eligible-peers")
    def human_advice_peers(
        request: Request, tenant: str, context_plan_id: str, limit: int = 50, cursor: str | None = None
    ):
        return human_advice.eligible_peers(
            auth.resolve(request), uuid(tenant), uuid(context_plan_id), limit, cursor
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/human-advice/{obj}")
    def human_advice_get(request: Request, tenant: str, obj: str):
        return human_advice.get(auth.resolve(request), uuid(tenant), uuid(obj))

    @app.get("/v1/tenants/{tenant}/ai-enablement/human-advice/{obj}/revisions")
    def human_advice_history(
        request: Request, tenant: str, obj: str, limit: int = 50, cursor: str | None = None
    ):
        return human_advice.history(auth.resolve(request), uuid(tenant), uuid(obj), limit, cursor)

    @app.get("/v1/tenants/{tenant}/ai-enablement/human-advice/{obj}/revisions/{revision_id}")
    def human_advice_revision(request: Request, tenant: str, obj: str, revision_id: str):
        return human_advice.get(auth.resolve(request), uuid(tenant), uuid(obj), uuid(revision_id))

    @app.post("/v1/tenants/{tenant}/ai-enablement/human-advice", status_code=201)
    async def human_advice_create(request: Request, tenant: str):
        body = await strict_body(request)
        validate("HumanAdviceCreate", body)
        return await run_in_threadpool(
            human_advice.save, auth.resolve(request), uuid(tenant), body, request.state.correlation
        )

    def advice_action(action):
        async def handler(request: Request, tenant: str, obj: str):
            body = await strict_body(request)
            # Only the closed, generated action routes below reach this handler.
            schema = "HumanAdvice" + "".join(piece.title() for piece in action.split("-"))
            validate(schema, body)
            return await run_in_threadpool(
                human_advice.save,
                auth.resolve(request),
                uuid(tenant),
                body,
                request.state.correlation,
                uuid(obj),
                action,
            )

        handler.__name__ = "human_advice_" + action.replace("-", "_")
        return handler

    for action in HUMAN_ADVICE_ACTIONS:
        app.add_api_route(
            "/v1/tenants/{tenant}/ai-enablement/human-advice/{obj}/actions/" + action,
            advice_action(action),
            methods=["POST"],
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/catalog")
    def ai_catalog(request: Request, tenant: str):
        return ai_enablement.catalog(auth.resolve(request), uuid(tenant))

    @app.get("/v1/tenants/{tenant}/ai-enablement/policy")
    def ai_policy_get(request: Request, tenant: str):
        return ai_policy.get(auth.resolve(request), uuid(tenant))

    @app.get("/v1/tenants/{tenant}/ai-enablement/policy/revisions")
    def ai_policy_revisions(request: Request, tenant: str, limit: int = 50, cursor: str | None = None):
        return ai_policy.revisions(auth.resolve(request), uuid(tenant), limit, cursor)

    @app.put("/v1/tenants/{tenant}/ai-enablement/policy")
    async def ai_policy_update(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AIPolicyCommand", body)
        return await run_in_threadpool(
            ai_policy.save, auth.resolve(request), uuid(tenant), body, request.state.correlation
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/ranking-weights")
    def ai_ranking_weights_get(request: Request, tenant: str):
        return ai_ranking.get(auth.resolve(request), uuid(tenant))

    @app.put("/v1/tenants/{tenant}/ai-enablement/ranking-weights")
    async def ai_ranking_weights_update(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AIRankingWeightsCommand", body)
        return await run_in_threadpool(
            ai_ranking.save, auth.resolve(request), uuid(tenant), body, request.state.correlation
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/ranking")
    async def ai_ranking_create(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AIRankingRequest", body)
        return await run_in_threadpool(ai_ranking.rank, auth.resolve(request), uuid(tenant), body["profile"])

    @app.get("/v1/tenants/{tenant}/ai-enablement/solutions")
    def ai_solutions(request: Request, tenant: str):
        return ai_enablement.solutions(auth.resolve(request), uuid(tenant))

    @app.get("/v1/tenants/{tenant}/ai-enablement/solution-shortlist")
    def ai_solution_shortlist(request: Request, tenant: str, opportunity_id: str, expanded: bool = False):
        return ai_enablement.solution_shortlist(auth.resolve(request), uuid(tenant), opportunity_id, expanded)

    @app.get("/v1/public/ai-vetting-criteria")
    def public_ai_vetting_criteria():
        return ai_enablement.public_vetting()

    @app.get("/v1/public/ai-solution-disclosures")
    def public_ai_solution_disclosures():
        return ai_enablement.public_disclosures()

    @app.get("/v1/tenants/{tenant}/ai-enablement/solution-fit-scores")
    def ai_solution_fit_score_list(request: Request, tenant: str, opportunity_id: str):
        return ai_solution_fit_scores.list(auth.resolve(request), uuid(tenant), opportunity_id)

    @app.post("/v1/tenants/{tenant}/ai-enablement/solution-fit-scores", status_code=201)
    async def ai_solution_fit_score_create(request: Request, tenant: str):
        body = await strict_body(request)
        return ai_solution_fit_scores.create(
            auth.resolve(request), uuid(tenant), body, request.state.correlation
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/task-templates")
    def ai_task_templates(request: Request, tenant: str):
        return ai_enablement.task_templates(auth.resolve(request), uuid(tenant))

    @app.get("/v1/tenants/{tenant}/ai-enablement/diagnoses")
    def ai_diagnosis_list(request: Request, tenant: str, limit: int = 50, cursor: str | None = None):
        return ai_diagnoses.listing(auth.resolve(request), uuid(tenant), limit, cursor)

    @app.get("/v1/tenants/{tenant}/ai-enablement/diagnoses/{obj}")
    def ai_diagnosis_get(request: Request, tenant: str, obj: str):
        return ai_diagnoses.get(auth.resolve(request), uuid(tenant), uuid(obj))

    @app.get("/v1/tenants/{tenant}/ai-enablement/diagnoses/{obj}/revisions")
    def ai_diagnosis_history(
        request: Request, tenant: str, obj: str, limit: int = 50, cursor: str | None = None
    ):
        return ai_diagnoses.history(auth.resolve(request), uuid(tenant), uuid(obj), limit, cursor)

    @app.get("/v1/tenants/{tenant}/ai-enablement/diagnoses/{obj}/revisions/{revision_id}")
    def ai_diagnosis_revision(request: Request, tenant: str, obj: str, revision_id: str):
        return ai_diagnoses.get(auth.resolve(request), uuid(tenant), uuid(obj), uuid(revision_id))

    @app.post("/v1/tenants/{tenant}/ai-enablement/diagnoses", status_code=201)
    async def ai_diagnosis_create(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AIDiagnosisCreate", body)
        return await run_in_threadpool(
            ai_diagnoses.command, auth.resolve(request), uuid(tenant), body, request.state.correlation
        )

    @app.put("/v1/tenants/{tenant}/ai-enablement/diagnoses/{obj}")
    async def ai_diagnosis_update(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        validate("AIDiagnosisUpdate", body)
        return await run_in_threadpool(
            ai_diagnoses.command,
            auth.resolve(request),
            uuid(tenant),
            body,
            request.state.correlation,
            uuid(obj),
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/diagnoses/{obj}/actions/complete")
    async def ai_diagnosis_complete(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        validate("AIDiagnosisComplete", body)
        return await run_in_threadpool(
            ai_diagnoses.command,
            auth.resolve(request),
            uuid(tenant),
            body,
            request.state.correlation,
            uuid(obj),
            "complete",
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/diagnoses/{obj}/actions/revise")
    async def ai_diagnosis_revise(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        validate("AIDiagnosisRevise", body)
        return await run_in_threadpool(
            ai_diagnoses.command,
            auth.resolve(request),
            uuid(tenant),
            body,
            request.state.correlation,
            uuid(obj),
            "revise",
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/diagnoses/{obj}/contributor-invitations")
    def ai_diagnosis_contributor_invitations(request: Request, tenant: str, obj: str):
        return ai_diagnosis_contributions.list_invitations(auth.resolve(request), uuid(tenant), uuid(obj))

    @app.post(
        "/v1/tenants/{tenant}/ai-enablement/diagnoses/{obj}/contributor-invitations",
        status_code=201,
    )
    async def ai_diagnosis_contributor_invitation_create(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        validate("AIDiagnosisContributorInvitationCreate", body)
        return await run_in_threadpool(
            ai_diagnosis_contributions.create_invitation,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            body,
            request.state.correlation,
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/diagnoses/{obj}/contributions")
    def ai_diagnosis_contributions_list(request: Request, tenant: str, obj: str):
        return ai_diagnosis_contributions.list_contributions(auth.resolve(request), uuid(tenant), uuid(obj))

    @app.post(
        "/v1/tenants/{tenant}/ai-enablement/diagnoses/{obj}/contributions",
        status_code=201,
    )
    async def ai_diagnosis_contribution_submit(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        validate("AIDiagnosisContributionSubmit", body)
        return await run_in_threadpool(
            ai_diagnosis_contributions.submit,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            body,
            request.state.correlation,
        )

    @app.post(
        "/v1/tenants/{tenant}/ai-enablement/diagnoses/{obj}/contributions/{contribution_id}/actions/accept"
    )
    async def ai_diagnosis_contribution_accept(request: Request, tenant: str, obj: str, contribution_id: str):
        body = await strict_body(request)
        validate("AIDiagnosisContributionDecision", body)
        return await run_in_threadpool(
            ai_diagnosis_contributions.decide,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            uuid(contribution_id),
            body,
            request.state.correlation,
            "ACCEPTED",
        )

    @app.post(
        "/v1/tenants/{tenant}/ai-enablement/diagnoses/{obj}/contributions/{contribution_id}/actions/reject"
    )
    async def ai_diagnosis_contribution_reject(request: Request, tenant: str, obj: str, contribution_id: str):
        body = await strict_body(request)
        validate("AIDiagnosisContributionRejection", body)
        return await run_in_threadpool(
            ai_diagnosis_contributions.decide,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            uuid(contribution_id),
            body,
            request.state.correlation,
            "REJECTED",
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/diagnoses/{obj}/advisor-reviews", status_code=201)
    async def ai_diagnosis_review_request(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        validate("AIDiagnosisReviewRequest", body)
        return await run_in_threadpool(
            ai_diagnosis_reviews.request,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            body,
            request.state.correlation,
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/diagnoses/{obj}/advisor-reviews")
    def ai_diagnosis_review_list(request: Request, tenant: str, obj: str):
        return ai_diagnosis_reviews.list_for_diagnosis(auth.resolve(request), uuid(tenant), uuid(obj))

    @app.get("/v1/tenants/{tenant}/ai-enablement/diagnosis-review-queue")
    def ai_diagnosis_review_queue(request: Request, tenant: str):
        return ai_diagnosis_reviews.queue(auth.resolve(request), uuid(tenant))

    @app.get("/v1/tenants/{tenant}/ai-enablement/diagnosis-reviews/{review_id}")
    def ai_diagnosis_review_get(request: Request, tenant: str, review_id: str):
        return ai_diagnosis_reviews.get(auth.resolve(request), uuid(tenant), uuid(review_id))

    async def diagnosis_review_action(request, tenant, review_id, schema, kind):
        body = await strict_body(request)
        validate(schema, body)
        return await run_in_threadpool(
            ai_diagnosis_reviews.act,
            auth.resolve(request),
            uuid(tenant),
            uuid(review_id),
            body,
            request.state.correlation,
            kind,
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/diagnosis-reviews/{review_id}/actions/start")
    async def ai_diagnosis_review_start(request: Request, tenant: str, review_id: str):
        return await diagnosis_review_action(request, tenant, review_id, "AIDiagnosisReviewAction", "STARTED")

    @app.post("/v1/tenants/{tenant}/ai-enablement/diagnosis-reviews/{review_id}/comments")
    async def ai_diagnosis_review_comment(request: Request, tenant: str, review_id: str):
        return await diagnosis_review_action(
            request, tenant, review_id, "AIDiagnosisReviewComment", "COMMENTED"
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/diagnosis-reviews/{review_id}/actions/validate")
    async def ai_diagnosis_review_validate(request: Request, tenant: str, review_id: str):
        return await diagnosis_review_action(
            request, tenant, review_id, "AIDiagnosisReviewAction", "VALIDATED"
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/problem-baselines")
    def ai_problem_baseline_list(request: Request, tenant: str, limit: int = 50, cursor: str | None = None):
        return ai_problem_baselines.listing(auth.resolve(request), uuid(tenant), limit, cursor)

    @app.post("/v1/tenants/{tenant}/ai-enablement/outcome-observations", status_code=201)
    async def ai_outcome_observation_create(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AICurrentOutcomeObservationCreate", body)
        return await run_in_threadpool(
            ai_outcome_observations.create,
            auth.resolve(request),
            uuid(tenant),
            body,
            request.state.correlation,
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/outcome-sharing-consents", status_code=201)
    async def ai_outcome_sharing_consent_create(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AIOutcomeSharingConsentCreate", body)
        return await run_in_threadpool(
            ai_outcome_evidence.consent, auth.resolve(request), uuid(tenant), body, request.state.correlation
        )

    @app.get("/v1/platform/outcome-evidence-publications")
    def ai_outcome_evidence_publication_list(request: Request):
        return ai_outcome_evidence.listing(auth.resolve(request))

    @app.post("/v1/platform/outcome-evidence-publications", status_code=201)
    async def ai_outcome_evidence_publication_prepare(request: Request):
        body = await strict_body(request)
        validate("AIOutcomeEvidencePrepare", body)
        return await run_in_threadpool(ai_outcome_evidence.prepare, auth.resolve(request), body)

    @app.post("/v1/platform/outcome-evidence-publications/{publication_id}/actions/{action}", status_code=201)
    async def ai_outcome_evidence_publication_action(request: Request, publication_id: str, action: str):
        body = await strict_body(request)
        validate("AIOutcomeEvidenceAction", body)
        return await run_in_threadpool(
            ai_outcome_evidence.action, auth.resolve(request), uuid(publication_id), action, body
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/outcomes-dashboard")
    def ai_outcomes_dashboard_get(
        request: Request,
        tenant: str,
        plan_id: str,
        baseline_object_id: str,
        opportunity_id: str,
    ):
        return ai_outcome_observations.dashboard(
            auth.resolve(request),
            uuid(tenant),
            uuid(plan_id),
            uuid(baseline_object_id),
            opportunity_id,
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/sponsor-value-reports", status_code=201)
    async def ai_sponsor_value_report_create(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AISponsorValueReportCreate", body)
        return await run_in_threadpool(
            ai_sponsor_value_reports.create,
            auth.resolve(request),
            uuid(tenant),
            body,
            request.state.correlation,
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/sponsor-value-reports/{obj}")
    def ai_sponsor_value_report_get(request: Request, tenant: str, obj: str):
        return ai_sponsor_value_reports.get(auth.resolve(request), uuid(tenant), uuid(obj))

    @app.post("/v1/tenants/{tenant}/ai-enablement/quarterly-value-reviews", status_code=201)
    async def ai_quarterly_value_review_start(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AIQuarterlyValueReviewStart", body)
        return await run_in_threadpool(
            ai_quarterly_value_reviews.start,
            auth.resolve(request),
            uuid(tenant),
            body,
            request.state.correlation,
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/quarterly-value-reviews/{review_id}")
    def ai_quarterly_value_review_get(request: Request, tenant: str, review_id: str):
        return ai_quarterly_value_reviews.get(auth.resolve(request), uuid(tenant), uuid(review_id))

    @app.post(
        "/v1/tenants/{tenant}/ai-enablement/quarterly-value-reviews/{review_id}/agreements", status_code=201
    )
    async def ai_quarterly_value_review_agreement(request: Request, tenant: str, review_id: str):
        body = await strict_body(request)
        validate("AIQuarterlyValueReviewAgreementCreate", body)
        return await run_in_threadpool(
            ai_quarterly_value_reviews.agreement,
            auth.resolve(request),
            uuid(tenant),
            uuid(review_id),
            body,
            request.state.correlation,
        )

    @app.post(
        "/v1/tenants/{tenant}/ai-enablement/quarterly-value-reviews/{review_id}/actions", status_code=201
    )
    async def ai_quarterly_value_review_action(request: Request, tenant: str, review_id: str):
        body = await strict_body(request)
        validate("AIQuarterlyValueReviewActionCreate", body)
        return await run_in_threadpool(
            ai_quarterly_value_reviews.action,
            auth.resolve(request),
            uuid(tenant),
            uuid(review_id),
            body,
            request.state.correlation,
        )

    @app.post(
        "/v1/tenants/{tenant}/ai-enablement/quarterly-value-reviews/{review_id}/actions/{action_id}/progress",
        status_code=201,
    )
    async def ai_quarterly_value_review_progress(
        request: Request, tenant: str, review_id: str, action_id: str
    ):
        body = await strict_body(request)
        validate("AIQuarterlyValueReviewActionProgress", body)
        return await run_in_threadpool(
            ai_quarterly_value_reviews.action,
            auth.resolve(request),
            uuid(tenant),
            uuid(review_id),
            body,
            request.state.correlation,
            uuid(action_id),
        )

    @app.post(
        "/v1/tenants/{tenant}/ai-enablement/quarterly-value-reviews/{review_id}/actions/complete",
        status_code=201,
    )
    async def ai_quarterly_value_review_complete(request: Request, tenant: str, review_id: str):
        body = await strict_body(request)
        validate("AIQuarterlyValueReviewComplete", body)
        return await run_in_threadpool(
            ai_quarterly_value_reviews.complete,
            auth.resolve(request),
            uuid(tenant),
            uuid(review_id),
            body,
            request.state.correlation,
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/next-opportunities")
    def ai_next_opportunity_list(request: Request, tenant: str):
        return ai_next_opportunities.listing(auth.resolve(request), uuid(tenant))

    @app.post(
        "/v1/tenants/{tenant}/ai-enablement/next-opportunities/{suggestion_id}/actions/take-up",
        status_code=201,
    )
    async def ai_next_opportunity_take_up(request: Request, tenant: str, suggestion_id: str):
        body = await strict_body(request)
        validate("AINextOpportunityTakeUp", body)
        return await run_in_threadpool(
            ai_next_opportunities.take_up,
            auth.resolve(request),
            uuid(tenant),
            uuid(suggestion_id),
            body,
            request.state.correlation,
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/diagnoses/{obj}/opportunity-map")
    def ai_opportunity_map_get(request: Request, tenant: str, obj: str, revision_id: str | None = None):
        return ai_opportunity_mapping.get(
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            uuid(revision_id) if revision_id is not None else None,
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/diagnoses/{obj}/opportunity-ranking")
    async def ai_mapped_opportunity_ranking(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        validate("AIMappedOpportunityRankingRequest", body)
        return await run_in_threadpool(
            ai_ranking.rank_mapping,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            uuid(body["revision_id"]),
            body["profile"],
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/problem-baselines/{obj}")
    def ai_problem_baseline_get(request: Request, tenant: str, obj: str):
        return ai_problem_baselines.get(auth.resolve(request), uuid(tenant), uuid(obj))

    @app.get("/v1/tenants/{tenant}/ai-enablement/problem-baselines/{obj}/revisions")
    def ai_problem_baseline_history(
        request: Request, tenant: str, obj: str, limit: int = 50, cursor: str | None = None
    ):
        return ai_problem_baselines.history(auth.resolve(request), uuid(tenant), uuid(obj), limit, cursor)

    @app.get("/v1/tenants/{tenant}/ai-enablement/problem-baselines/{obj}/revisions/{revision_id}")
    def ai_problem_baseline_revision(request: Request, tenant: str, obj: str, revision_id: str):
        return ai_problem_baselines.get(auth.resolve(request), uuid(tenant), uuid(obj), uuid(revision_id))

    @app.post("/v1/tenants/{tenant}/ai-enablement/problem-baselines", status_code=201)
    async def ai_problem_baseline_create(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AIProblemBaselineCreate", body)
        return await run_in_threadpool(
            ai_problem_baselines.command,
            auth.resolve(request),
            uuid(tenant),
            body,
            request.state.correlation,
        )

    @app.put("/v1/tenants/{tenant}/ai-enablement/problem-baselines/{obj}")
    async def ai_problem_baseline_update(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        validate("AIProblemBaselineUpdate", body)
        return await run_in_threadpool(
            ai_problem_baselines.command,
            auth.resolve(request),
            uuid(tenant),
            body,
            request.state.correlation,
            uuid(obj),
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/problem-baselines/{obj}/actions/lock")
    async def ai_problem_baseline_lock(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        validate("AIProblemBaselineLock", body)
        return await run_in_threadpool(
            ai_problem_baselines.command,
            auth.resolve(request),
            uuid(tenant),
            body,
            request.state.correlation,
            uuid(obj),
            "lock",
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/plans")
    def ai_plan_list(request: Request, tenant: str, limit: int = 50, cursor: str | None = None):
        return ai_plans.listing(auth.resolve(request), uuid(tenant), limit, cursor)

    @app.get("/v1/tenants/{tenant}/ai-enablement/plans/{obj}")
    def ai_plan_get(request: Request, tenant: str, obj: str):
        return ai_plans.get(auth.resolve(request), uuid(tenant), uuid(obj))

    @app.get("/v1/tenants/{tenant}/ai-enablement/plans/{obj}/revisions/{revision_id}/guidance")
    def ai_plan_guidance(request: Request, tenant: str, obj: str, revision_id: str):
        return ai_plans.guidance(auth.resolve(request), uuid(tenant), uuid(obj), uuid(revision_id))

    @app.post("/v1/tenants/{tenant}/ai-enablement/plans/{obj}/revisions/{revision_id}/exports")
    async def ai_plan_export(request: Request, tenant: str, obj: str, revision_id: str):
        body = await strict_body(request)
        validate("AIPlanExportRequest", body)
        return await run_in_threadpool(
            ai_plan_exports.create,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            uuid(revision_id),
            body,
            request.state.correlation,
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/plans/{obj}/revisions")
    def ai_plan_history(request: Request, tenant: str, obj: str, limit: int = 50, cursor: str | None = None):
        return ai_plans.history(auth.resolve(request), uuid(tenant), uuid(obj), limit, cursor)

    @app.post("/v1/tenants/{tenant}/ai-enablement/plans", status_code=201)
    async def ai_plan_create(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AIAdoptionPlanCreate", body)
        return await run_in_threadpool(
            ai_plans.save, auth.resolve(request), uuid(tenant), body, request.state.correlation
        )

    @app.put("/v1/tenants/{tenant}/ai-enablement/plans/{obj}")
    async def ai_plan_update(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        validate("AIAdoptionPlanUpdate", body)
        return await run_in_threadpool(
            ai_plans.save, auth.resolve(request), uuid(tenant), body, request.state.correlation, uuid(obj)
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/plans/{obj}/deployment/actions/generate")
    async def ai_deployment_generate(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        validate("AIDeploymentGenerate", body)
        return await run_in_threadpool(
            ai_plans.deployment,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            body,
            request.state.correlation,
            "generate",
        )

    @app.put("/v1/tenants/{tenant}/ai-enablement/plans/{obj}/deployment/milestones/{milestone_code}")
    async def ai_deployment_progress(request: Request, tenant: str, obj: str, milestone_code: str):
        body = await strict_body(request)
        validate("AIDeploymentProgress", body)
        return await run_in_threadpool(
            ai_plans.deployment,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            body,
            request.state.correlation,
            "progress",
            milestone_code,
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/plans/{obj}/deployment/actions/complete")
    async def ai_deployment_complete(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        validate("AIDeploymentComplete", body)
        return await run_in_threadpool(
            ai_plans.deployment,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            body,
            request.state.correlation,
            "complete",
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/plans/{obj}/deployment/actions/attest")
    async def ai_deployment_attest(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        validate("AITrainingDeploymentAttest", body)
        return await run_in_threadpool(
            ai_plans.attest_deployment,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            body,
            request.state.correlation,
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/plans/{obj}/role-training")
    async def ai_role_training_get(request: Request, tenant: str, obj: str, solution_id: str):
        return await run_in_threadpool(
            ai_role_training.get,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            solution_id,
        )

    @app.post(
        "/v1/tenants/{tenant}/ai-enablement/plans/{obj}/role-training/modules/{module_key}/actions/complete"
    )
    async def ai_role_training_complete(request: Request, tenant: str, obj: str, module_key: str):
        body = await strict_body(request)
        validate("AIRoleTrainingComplete", body)
        return await run_in_threadpool(
            ai_role_training.complete,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            module_key,
            body,
            request.state.correlation,
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/plans/{obj}/champion-appointments")
    async def ai_champion_appointments_list(request: Request, tenant: str, obj: str):
        return await run_in_threadpool(
            ai_champion_appointments.listing,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
        )

    @app.post(
        "/v1/tenants/{tenant}/ai-enablement/plans/{obj}/champion-appointments",
        status_code=201,
    )
    async def ai_champion_appointment_create(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        validate("AIChampionAppointmentCreate", body)
        return await run_in_threadpool(
            ai_champion_appointments.create,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            body,
            request.state.correlation,
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/plans/{obj}/champion-guide")
    async def ai_champion_guide_get(request: Request, tenant: str, obj: str, solution_id: str):
        return await run_in_threadpool(
            ai_champion_appointments.guide,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            solution_id,
        )

    @app.put("/v1/tenants/{tenant}/ai-enablement/plans/{obj}/impact-reference")
    async def ai_impact_reference_save(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        validate("AIImpactReferenceCommand", body)
        return await run_in_threadpool(
            ai_impact.save,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            body,
            request.state.correlation,
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/plans/{obj}/impact-reference/result")
    def ai_impact_reference_result(request: Request, tenant: str, obj: str):
        return ai_impact.result(auth.resolve(request), uuid(tenant), uuid(obj))

    @app.post("/v1/tenants/{tenant}/ai-enablement/assessment")
    async def ai_assessment(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AIAssessmentRequest", body)
        return await run_in_threadpool(
            ai_enablement.assessment, auth.resolve(request), uuid(tenant), body["profile"]
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/advisory")
    async def ai_advisory(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AIAdvisoryRequest", body)
        return await run_in_threadpool(
            ai_enablement.advisory, auth.resolve(request), uuid(tenant), body, request.state.correlation
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/advisory-jobs", status_code=202)
    async def create_ai_advisory_job(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AIAdvisoryRequest", body)
        return await run_in_threadpool(ai_jobs.submit, auth.resolve(request), uuid(tenant), body)

    @app.get("/v1/tenants/{tenant}/ai-enablement/advisory-jobs/{job}")
    def get_ai_advisory_job(request: Request, tenant: str, job: str):
        return ai_jobs.status(auth.resolve(request), uuid(tenant), uuid(job))

    @app.post("/v1/tenants/{tenant}/ai-enablement/advisory-jobs/{job}/actions/cancel")
    def cancel_ai_advisory_job(request: Request, tenant: str, job: str):
        return ai_jobs.cancel(auth.resolve(request), uuid(tenant), uuid(job))

    @app.post("/v1/tenants/{tenant}/ai-enablement/forecasts")
    async def create_ai_forecast(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AIForecastRequest", body)
        return ai_forecasts.create(auth.resolve(request), uuid(tenant), body)

    @app.get("/v1/tenants/{tenant}/ai-enablement/forecasts/{scenario}")
    def get_ai_forecast(request: Request, tenant: str, scenario: str, version: int | None = None):
        return ai_forecasts.get(auth.resolve(request), uuid(tenant), uuid(scenario), version)

    @app.get("/v1/tenants/{tenant}/ai-enablement/forecasts/{scenario}/export")
    def export_ai_forecast(request: Request, tenant: str, scenario: str, version: int | None = None):
        return ai_forecasts.export(auth.resolve(request), uuid(tenant), uuid(scenario), version)

    @app.post(
        "/v1/tenants/{tenant}/ai-enablement/forecasts/{scenario}/versions/{version}/actions/request-adoption"
    )
    def request_ai_forecast_adoption(request: Request, tenant: str, scenario: str, version: int):
        return ai_forecasts.request_adoption(auth.resolve(request), uuid(tenant), uuid(scenario), version)

    @app.post("/v1/tenants/{tenant}/ai-enablement/safety-feedback")
    async def create_ai_safety_feedback(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AISafetyFeedbackRequest", body)
        return ai_safety.feedback(auth.resolve(request), uuid(tenant), body)

    @app.get("/v1/tenants/{tenant}/ai-enablement/safety-shutdowns")
    def get_ai_safety_shutdowns(request: Request, tenant: str):
        return ai_safety.status(auth.resolve(request), uuid(tenant))

    @app.post("/v1/tenants/{tenant}/ai-enablement/safety-shutdowns")
    async def manage_ai_safety_shutdown(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AIShutdownRequest", body)
        return ai_safety.change(auth.resolve(request), uuid(tenant), body)

    @app.post("/v1/tenants/{tenant}/ai-enablement/safety-shutdowns/{event}/actions/approve-recovery")
    async def approve_ai_safety_recovery(request: Request, tenant: str, event: str):
        body = await strict_body(request)
        validate("AIRecoveryApprovalRequest", body)
        return ai_safety.approve_recovery(auth.resolve(request), uuid(tenant), uuid(event), body)

    @app.post("/v1/tenants/{tenant}/ai-enablement/extractions")
    async def create_ai_extraction(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AIExtractionRequest", body)
        return await run_in_threadpool(
            ai_extraction.create,
            auth.resolve(request),
            uuid(tenant),
            body,
            request.state.correlation,
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/extractions/{draft}/actions/apply")
    async def review_ai_extraction(request: Request, tenant: str, draft: str):
        body = await strict_body(request)
        validate("AIExtractionApplyRequest", body)
        return ai_extraction.apply(auth.resolve(request), uuid(tenant), uuid(draft), body)

    @app.post("/v1/tenants/{tenant}/ai-enablement/indicator-design/proposals")
    async def create_ai_indicator_proposal(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AIIndicatorProposalRequest", body)
        return ai_indicator_design.propose(auth.resolve(request), uuid(tenant), body)

    @app.post("/v1/tenants/{tenant}/ai-enablement/indicator-design/drafts")
    async def create_ai_indicator_draft(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AIIndicatorDraftRequest", body)
        return ai_indicator_design.create_draft(
            auth.resolve(request), uuid(tenant), body, request.state.correlation
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/cost-comparison")
    async def ai_cost_comparison(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AICostComparisonRequest", body)
        return await run_in_threadpool(
            ai_enablement.cost_comparison, auth.resolve(request), uuid(tenant), body
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/value-case")
    async def ai_value_case(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AIValueCaseRequest", body)
        return await run_in_threadpool(ai_enablement.value_case, auth.resolve(request), uuid(tenant), body)

    @app.post("/v1/tenants/{tenant}/ai-enablement/value-case/export")
    async def ai_value_case_export(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AIValueCaseExportRequest", body)
        return await run_in_threadpool(
            ai_enablement.value_case_export, auth.resolve(request), uuid(tenant), body
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/value-cases", status_code=201)
    async def ai_value_case_version_create(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AIValueCaseVersionCreate", body)
        return await run_in_threadpool(
            ai_value_cases.command,
            auth.resolve(request),
            uuid(tenant),
            body,
            request.state.correlation,
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/value-cases/{obj}")
    def ai_value_case_version_get(request: Request, tenant: str, obj: str):
        return ai_value_cases.get(auth.resolve(request), uuid(tenant), uuid(obj))

    @app.get("/v1/tenants/{tenant}/ai-enablement/value-cases/{obj}/revisions/{revision_id}")
    def ai_value_case_revision_get(request: Request, tenant: str, obj: str, revision_id: str):
        return ai_value_cases.get(auth.resolve(request), uuid(tenant), uuid(obj), uuid(revision_id))

    async def value_case_version_action(request: Request, tenant: str, obj: str, action: str, schema: str):
        body = await strict_body(request)
        validate(schema, body)
        return await run_in_threadpool(
            ai_value_cases.command,
            auth.resolve(request),
            uuid(tenant),
            body,
            request.state.correlation,
            uuid(obj),
            action,
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/value-cases/{obj}/actions/approve")
    async def ai_value_case_approve(request: Request, tenant: str, obj: str):
        return await value_case_version_action(request, tenant, obj, "approve", "AIValueCaseVersionLock")

    @app.post("/v1/tenants/{tenant}/ai-enablement/value-cases/{obj}/actions/lock")
    async def ai_value_case_baseline_lock(request: Request, tenant: str, obj: str):
        return await value_case_version_action(request, tenant, obj, "lock", "AIValueCaseVersionLock")

    @app.post("/v1/tenants/{tenant}/ai-enablement/value-cases/{obj}/actions/revise")
    async def ai_value_case_revise(request: Request, tenant: str, obj: str):
        return await value_case_version_action(request, tenant, obj, "revise", "AIValueCaseVersionRevise")

    @app.post("/v1/tenants/{tenant}/ai-enablement/pilot-evaluation")
    async def ai_pilot_evaluation(request: Request, tenant: str):
        body = await strict_body(request)
        validate("AIPilotEvaluationRequest", body)
        return await run_in_threadpool(
            ai_enablement.pilot_evaluation, auth.resolve(request), uuid(tenant), body
        )

    @app.get("/v1/tenants/{tenant}/frameworks/{obj}/completeness")
    def framework_completeness(request: Request, tenant: str, obj: str):
        return service.planning.read(auth.resolve(request), uuid(tenant), "framework_completeness", uuid(obj))

    def logframe_response(request, tenant, obj, revision_id, format):
        framework_id = uuid(obj)
        body, digest = LogframeExports(service).download(
            auth.resolve(request),
            uuid(tenant),
            framework_id,
            uuid(revision_id),
            format,
            request.state.correlation,
        )
        return Response(
            body,
            media_type=LOGFRAME_MEDIA[format],
            headers={
                "ETag": '"' + digest + '"',
                "Content-Disposition": 'attachment; filename="impact-logframe-'
                + framework_id[:8]
                + "."
                + format.lower()
                + '"',
            },
        )

    @app.get("/v1/tenants/{tenant}/frameworks/{obj}/logframe.csv")
    def logframe_csv(request: Request, tenant: str, obj: str, revision_id: str):
        return logframe_response(request, tenant, obj, revision_id, "CSV")

    @app.get("/v1/tenants/{tenant}/frameworks/{obj}/logframe.xlsx")
    def logframe_xlsx(request: Request, tenant: str, obj: str, revision_id: str):
        return logframe_response(request, tenant, obj, revision_id, "XLSX")

    @app.get("/v1/tenants/{tenant}/programmes/{obj}/targets-vs-actuals")
    def targets_vs_actuals(
        request: Request,
        tenant: str,
        obj: str,
        limit: int = 50,
        cursor: str | None = None,
        period_id: str | None = None,
    ):
        return service.planning.read(
            auth.resolve(request),
            uuid(tenant),
            "programme_targets_vs_actuals",
            uuid(obj),
            limit=limit,
            cursor=cursor,
            period_id=uuid(period_id) if period_id else None,
        )

    @app.get("/v1/tenants/{tenant}/programmes/{obj}/dashboard")
    def programme_dashboard(
        request: Request,
        tenant: str,
        obj: str,
        period_id: str | None = None,
        limit: int = 50,
        cursor: str | None = None,
    ):
        return dashboards.read(
            auth.resolve(request),
            uuid(tenant),
            "programme_dashboard",
            uuid(obj),
            limit=limit,
            cursor=cursor,
            period_id=uuid(period_id) if period_id else None,
        )

    @app.get("/v1/tenants/{tenant}/indicator-instances/{obj}/dashboard-series")
    def indicator_dashboard_series(
        request: Request, tenant: str, obj: str, limit: int = 50, cursor: str | None = None
    ):
        return dashboards.read(
            auth.resolve(request),
            uuid(tenant),
            "indicator_dashboard_series",
            uuid(obj),
            limit=limit,
            cursor=cursor,
        )

    @app.get("/v1/tenants/{tenant}/indicator-instances/{obj}/dashboard-sources")
    def indicator_dashboard_sources(
        request: Request,
        tenant: str,
        obj: str,
        period_id: str | None = None,
        limit: int = 50,
        cursor: str | None = None,
    ):
        return dashboards.read(
            auth.resolve(request),
            uuid(tenant),
            "indicator_dashboard_sources",
            uuid(obj),
            limit=limit,
            cursor=cursor,
            period_id=uuid(period_id) if period_id else None,
        )

    @app.get("/v1/tenants/{tenant}/indicator-definitions/{obj}/portfolio")
    def indicator_definition_portfolio(
        request: Request,
        tenant: str,
        obj: str,
        period_id: str | None = None,
        limit: int = 50,
        cursor: str | None = None,
    ):
        return dashboards.read(
            auth.resolve(request),
            uuid(tenant),
            "indicator_definition_portfolio",
            uuid(obj),
            limit=limit,
            cursor=cursor,
            period_id=uuid(period_id) if period_id else None,
        )

    @app.get("/v1/tenants/{tenant}/publication-recipients")
    def publication_recipients(request: Request, tenant: str):
        return service.reporting.recipients(auth.resolve(request), uuid(tenant))

    @app.get("/v1/tenants/{tenant}/reports/{obj}/export")
    def report_export(request: Request, tenant: str, obj: str):
        report_id = uuid(obj)
        body, digest = service.reporting.export(auth.resolve(request), uuid(tenant), report_id)
        return HTMLResponse(
            body,
            headers={
                "ETag": '"' + digest + '"',
                "Content-Disposition": 'inline; filename="impact-report-' + report_id[:8] + '.html"',
                "Content-Security-Policy": REPORT_CSP,
            },
        )

    @app.get("/v1/tenants/{tenant}/reports/{obj}/export.csv")
    def report_export_csv(request: Request, tenant: str, obj: str):
        report_id = uuid(obj)
        body, digest = service.reporting.export(auth.resolve(request), uuid(tenant), report_id, format="CSV")
        return Response(
            body,
            media_type="text/csv",
            headers={
                "ETag": '"' + digest + '"',
                "Content-Disposition": 'attachment; filename="impact-report-' + report_id[:8] + '.csv"',
            },
        )

    @app.get("/v1/tenants/{tenant}/publications/{obj}/view")
    def publication_view(request: Request, tenant: str, obj: str):
        artifact = service.reporting.publication(
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            "HTML",
            request.state.correlation,
        )
        return Response(
            artifact["body"],
            media_type=artifact["media_type"],
            headers={
                "ETag": '"' + artifact["digest"] + '"',
                "Content-Disposition": 'inline; filename="' + artifact["filename"] + '"',
                "Content-Security-Policy": REPORT_CSP,
            },
        )

    @app.get("/v1/tenants/{tenant}/publications/{obj}/download.csv")
    def publication_download_csv(request: Request, tenant: str, obj: str):
        artifact = service.reporting.publication(
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            "CSV",
            request.state.correlation,
        )
        return Response(
            artifact["body"],
            media_type=artifact["media_type"],
            headers={
                "ETag": '"' + artifact["digest"] + '"',
                "Content-Disposition": 'attachment; filename="' + artifact["filename"] + '"',
            },
        )

    # Evidence uploads and mediated content (v0.22). Registered before the generic routes so that
    # "uploads" never reaches the domain dispatcher.
    @app.post("/v1/tenants/{tenant}/uploads", status_code=201)
    async def create_upload(request: Request, tenant: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            service.evidence.create_upload,
            auth.resolve(request),
            uuid(tenant),
            body,
            request.state.correlation,
        )

    @app.get("/v1/tenants/{tenant}/uploads/{obj}")
    def upload_status(request: Request, tenant: str, obj: str):
        return service.evidence.upload(auth.resolve(request), uuid(tenant), uuid(obj))

    @app.put("/v1/tenants/{tenant}/uploads/{obj}/content")
    async def upload_content(request: Request, tenant: str, obj: str):
        if request.headers.get("content-type", "").split(";")[0].strip() != "application/octet-stream":
            raise DomainError("VALIDATION_FAILED", 415)
        identity = await run_in_threadpool(auth.resolve, request)
        tenant_id, upload_id = uuid(tenant), uuid(obj)
        # Authorised and bounded by the declared size before the body is read.
        expected = await run_in_threadpool(service.evidence.content_limit, identity, tenant_id, upload_id)
        try:
            raw = await bounded_body(request, expected)
        except DomainError:
            raise DomainError("LIMIT_EXCEEDED", 413, reason="FILE_TOO_LARGE") from None
        return await run_in_threadpool(
            service.evidence.put_content, identity, tenant_id, upload_id, raw, request.state.correlation
        )

    @app.post("/v1/tenants/{tenant}/uploads/{obj}/actions/complete")
    async def complete_upload(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            service.evidence.complete,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            body,
            request.state.correlation,
        )

    @app.get("/v1/tenants/{tenant}/evidence/{obj}/content")
    def evidence_content(request: Request, tenant: str, obj: str, revision: str | None = None):
        artifact = service.evidence.content(
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            uuid(revision) if revision else None,
            request.state.correlation,
        )
        ascii_name = re.sub(r"[^A-Za-z0-9._-]", "_", artifact["filename"])
        media = artifact["media_type"] + (
            "; charset=utf-8" if artifact["media_type"].startswith("text/") else ""
        )
        return Response(
            artifact["body"],
            media_type=media,
            headers={
                "ETag": '"' + artifact["digest"] + '"',
                "Content-Disposition": 'attachment; filename="'
                + ascii_name
                + "\"; filename*=UTF-8''"
                + quote(artifact["filename"], safe=""),
                # Nothing in a downloaded file runs in this origin, even if a browser renders it.
                "Content-Security-Policy": "default-src 'none'; sandbox",
                "Cross-Origin-Resource-Policy": "same-origin",
            },
        )

    @app.get("/v1/tenants/{tenant}/observations/{obj}/evidence")
    def observation_evidence(request: Request, tenant: str, obj: str):
        return service.evidence.attachments(auth.resolve(request), uuid(tenant), "Observation", uuid(obj))

    @app.get("/v1/tenants/{tenant}/calculated-results/{obj}/evidence")
    def result_evidence(request: Request, tenant: str, obj: str):
        return service.evidence.attachments(
            auth.resolve(request), uuid(tenant), "CalculatedResult", uuid(obj)
        )

    @app.get("/v1/tenants/{tenant}/calculated-results/{obj}/reproduction")
    def result_reproduction(request: Request, tenant: str, obj: str):
        return service.reproduce_calculation(
            auth.resolve(request), uuid(tenant), uuid(obj), request.state.correlation
        )

    @app.post("/v1/tenants/{tenant}/calculation-compatibility/preview")
    async def calculation_compatibility_preview(request: Request, tenant: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            service.calculation_compatibility.preview,
            auth.resolve(request),
            uuid(tenant),
            body,
            request.state.correlation,
        )

    @app.post("/v1/tenants/{tenant}/population-overlap/compute")
    async def population_overlap_compute(request: Request, tenant: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            service.population_overlap.compute,
            auth.resolve(request),
            uuid(tenant),
            body,
            request.state.correlation,
        )

    @app.post("/v1/tenants/{tenant}/hierarchical-aggregation/compute")
    async def hierarchical_aggregation_compute(request: Request, tenant: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            service.hierarchical_aggregation.compute,
            auth.resolve(request),
            uuid(tenant),
            body,
            request.state.correlation,
        )

    @app.post("/v1/tenants/{tenant}/dimension-crosswalks/{obj}/preview")
    async def dimension_crosswalk_preview(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            service.dimension_crosswalk.preview,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            body,
            request.state.correlation,
        )

    @app.post("/v1/tenants/{tenant}/formula-definitions/preview")
    async def formula_definition_preview(request: Request, tenant: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            service.formula_authoring.preview,
            auth.resolve(request),
            uuid(tenant),
            body,
            request.state.correlation,
        )

    @app.post("/v1/tenants/{tenant}/portfolio-allocation-views/{obj}/preview")
    async def portfolio_attribution_preview(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            service.portfolio_attribution.preview,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            body,
            request.state.correlation,
        )

    @app.post("/v1/tenants/{tenant}/sponsored-cohorts", status_code=201)
    async def sponsored_cohort_create(request: Request, tenant: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            sponsored_access.create,
            auth.resolve(request),
            uuid(tenant),
            body,
            request.state.correlation,
        )

    @app.post("/v1/tenants/{tenant}/sponsored-access/{enrolment}/actions/accept")
    async def sponsored_access_accept(request: Request, tenant: str, enrolment: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            sponsored_access.accept,
            auth.resolve(request),
            uuid(tenant),
            uuid(enrolment),
            body,
            request.state.correlation,
        )

    @app.get("/v1/tenants/{tenant}/sponsored-access")
    def sponsored_access_list(request: Request, tenant: str):
        return sponsored_access.active(auth.resolve(request), uuid(tenant))

    @app.get("/v1/tenants/{tenant}/effective-entitlements")
    def effective_entitlement_list(request: Request, tenant: str):
        return entitlement_view.read(auth.resolve(request), uuid(tenant))

    @app.get("/v1/tenants/{tenant}/service-packages")
    def service_package_list(request: Request, tenant: str):
        return service_packages.listing(auth.resolve(request), uuid(tenant))

    @app.post("/v1/tenants/{tenant}/subscriptions/{subscription}/service-packages")
    async def service_package_purchase(request: Request, tenant: str, subscription: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            service_packages.purchase,
            auth.resolve(request),
            uuid(tenant),
            uuid(subscription),
            body,
            request.state.correlation,
        )

    @app.post("/v1/tenants/{tenant}/billing-profile")
    async def billing_profile_configure(request: Request, tenant: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            tax_invoicing.configure,
            auth.resolve(request),
            uuid(tenant),
            body,
            request.state.correlation,
        )

    @app.post("/v1/tenants/{tenant}/commercial-invoices/{invoice}/actions/issue")
    async def commercial_invoice_issue(request: Request, tenant: str, invoice: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            tax_invoicing.issue,
            auth.resolve(request),
            uuid(tenant),
            uuid(invoice),
            body,
            request.state.correlation,
        )

    @app.get("/v1/tenants/{tenant}/commercial-invoices/{invoice}")
    def commercial_invoice_read(request: Request, tenant: str, invoice: str):
        return tax_invoicing.read(auth.resolve(request), uuid(tenant), uuid(invoice))

    @app.post("/v1/tenants/{tenant}/agreements")
    async def organisation_agreement_configure(request: Request, tenant: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            agreement_coverage.configure,
            auth.resolve(request),
            uuid(tenant),
            body,
            request.state.correlation,
        )

    @app.get("/v1/tenants/{tenant}/agreements")
    def organisation_agreement_read(request: Request, tenant: str):
        return agreement_coverage.read(auth.resolve(request), uuid(tenant))

    @app.post("/v1/tenants/{tenant}/access-checks/resources")
    async def access_check_resources(request: Request, tenant: str):
        body = await strict_body(request)
        return await run_in_threadpool(access_checks.permitted, auth.resolve(request), uuid(tenant), body)

    @app.post("/v1/tenants/{tenant}/grants/{grant_id}/field-policy")
    async def attach_grant_field_policy(request: Request, tenant: str, grant_id: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            fine_grained_access.attach,
            auth.resolve(request),
            uuid(tenant),
            str(uuid(grant_id)),
            body,
            request.state.correlation,
        )

    @app.post("/v1/tenants/{tenant}/access/effective/self")
    async def explain_own_access(request: Request, tenant: str):
        body = await strict_body(request)
        return await run_in_threadpool(effective_access.own, auth.resolve(request), uuid(tenant), body)

    @app.post("/v1/tenants/{tenant}/access/effective/simulations")
    async def simulate_member_access(request: Request, tenant: str):
        body = await strict_body(request)
        return await run_in_threadpool(effective_access.simulate, auth.resolve(request), uuid(tenant), body)

    @app.post("/v1/tenants/{tenant}/derivatives/{derivative_id}/revisions")
    async def create_derivative(tenant: str, derivative_id: str, request: Request):
        body = await strict_body(request)
        return await run_in_threadpool(
            permission_safe_derivatives.create,
            auth.resolve(request),
            uuid(tenant),
            str(uuid(derivative_id)),
            body,
        )

    @app.get("/v1/tenants/{tenant}/derivatives/{derivative_id}/revisions/{revision_id}")
    async def read_derivative(tenant: str, derivative_id: str, revision_id: str, request: Request):
        return await run_in_threadpool(
            permission_safe_derivatives.read,
            auth.resolve(request),
            uuid(tenant),
            str(uuid(derivative_id)),
            str(uuid(revision_id)),
        )

    @app.post("/v1/tenants/{tenant}/external-shares")
    async def create_external_share(tenant: str, request: Request):
        body = await strict_body(request)
        return await run_in_threadpool(external_shares.create, auth.resolve(request), uuid(tenant), body)

    @app.get("/v1/tenants/{tenant}/external-shares/{share_id}")
    async def read_external_share(tenant: str, share_id: str, request: Request):
        return await run_in_threadpool(
            external_shares.read, auth.resolve(request), uuid(tenant), str(uuid(share_id))
        )

    @app.post("/v1/tenants/{tenant}/external-shares/{share_id}/revocation")
    async def revoke_external_share(tenant: str, share_id: str, request: Request):
        return await run_in_threadpool(
            external_shares.revoke, auth.resolve(request), uuid(tenant), str(uuid(share_id))
        )

    @app.post("/v1/tenants/{tenant}/derivatives/{derivative_id}/revisions/{revision_id}/presentation-leases")
    async def issue_presentation_lease(tenant: str, derivative_id: str, revision_id: str, request: Request):
        return await run_in_threadpool(
            access_change_propagation.issue,
            auth.resolve(request),
            uuid(tenant),
            str(uuid(derivative_id)),
            str(uuid(revision_id)),
        )

    @app.get("/v1/tenants/{tenant}/presentation-leases/{lease_id}")
    async def validate_presentation_lease(tenant: str, lease_id: str, request: Request):
        return await run_in_threadpool(
            access_change_propagation.validate, auth.resolve(request), uuid(tenant), str(uuid(lease_id))
        )

    @app.get("/v1/tenants/{tenant}/ai-enablement/trials")
    def ai_trial_list(request: Request, tenant: str, opportunity_id: str):
        return ai_trials.list(auth.resolve(request), uuid(tenant), opportunity_id)

    @app.post("/v1/tenants/{tenant}/ai-enablement/trials", status_code=201)
    async def ai_trial_create(request: Request, tenant: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            ai_trials.create,
            auth.resolve(request),
            uuid(tenant),
            body,
            request.state.correlation,
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/trials/{trial_id}/results", status_code=201)
    async def ai_trial_result_create(request: Request, tenant: str, trial_id: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            ai_trials.record_result,
            auth.resolve(request),
            uuid(tenant),
            str(uuid(trial_id)),
            body,
            request.state.correlation,
        )

    @app.post("/v1/tenants/{tenant}/ai-enablement/value-cases/from-trial", status_code=201)
    async def ai_value_case_from_trial(request: Request, tenant: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            ai_trials.build_value_case, auth.resolve(request), uuid(tenant), body, request.state.correlation
        )

    @app.get("/v1/tenants/{tenant}/reports/{obj}/exports")
    def report_exports(request: Request, tenant: str, obj: str):
        return service.exports.listing(auth.resolve(request), uuid(tenant), uuid(obj))

    def export_response(artifact):
        return Response(
            artifact["body"],
            media_type=artifact["media_type"],
            headers={
                "ETag": '"' + artifact["digest"] + '"',
                "Content-Disposition": 'attachment; filename="' + artifact["filename"] + '"',
            },
        )

    @app.get("/v1/tenants/{tenant}/reports/{obj}/exports/{job}/download")
    def report_export_download(request: Request, tenant: str, obj: str, job: str):
        return export_response(
            service.exports.download(
                auth.resolve(request), uuid(tenant), uuid(obj), uuid(job), request.state.correlation
            )
        )

    @app.get("/v1/tenants/{tenant}/publications/{obj}/download.{extension}")
    def publication_download_export(request: Request, tenant: str, obj: str, extension: str):
        if extension not in {"pdf", "xlsx", "docx"}:
            raise DomainError("RESOURCE_UNAVAILABLE", 404)
        return export_response(
            service.exports.publication(
                auth.resolve(request), uuid(tenant), uuid(obj), extension.upper(), request.state.correlation
            )
        )

    # Data-subject requests and the retention schedule (v0.25 part B): purpose-bound privacy routes,
    # registered before the generic routes so that "privacy-cases" never reaches the dispatcher.
    @app.get("/v1/tenants/{tenant}/privacy-cases")
    def privacy_cases(
        request: Request, tenant: str, purpose: str | None = None, limit: int = 50, cursor: str | None = None
    ):
        return service.privacy.listing(auth.resolve(request), uuid(tenant), purpose, limit, cursor)

    @app.post("/v1/tenants/{tenant}/privacy-cases", status_code=201)
    async def create_privacy_case(request: Request, tenant: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            service.privacy.create, auth.resolve(request), uuid(tenant), body, request.state.correlation
        )

    @app.get("/v1/tenants/{tenant}/privacy-cases/{obj}")
    def privacy_case(request: Request, tenant: str, obj: str, purpose: str | None = None):
        return service.privacy.get(auth.resolve(request), uuid(tenant), uuid(obj), purpose)

    @app.patch("/v1/tenants/{tenant}/privacy-cases/{obj}")
    async def patch_privacy_case(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            service.privacy.patch,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            body,
            request.state.correlation,
        )

    @app.get("/v1/tenants/{tenant}/privacy-cases/{obj}/plan")
    def privacy_case_plan(request: Request, tenant: str, obj: str, purpose: str | None = None):
        return service.privacy.plan_view(auth.resolve(request), uuid(tenant), uuid(obj), purpose)

    @app.post("/v1/tenants/{tenant}/privacy-cases/{obj}/actions/{action}")
    async def privacy_case_action(request: Request, tenant: str, obj: str, action: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            service.privacy.action,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            action,
            body,
            request.state.correlation,
        )

    @app.get("/v1/tenants/{tenant}/privacy-cases/{obj}/export")
    def privacy_case_export(request: Request, tenant: str, obj: str, purpose: str | None = None):
        package = service.privacy.download(
            auth.resolve(request), uuid(tenant), uuid(obj), purpose, request.state.correlation
        )
        return Response(
            package["body"],
            media_type="application/json",
            headers={
                "ETag": '"' + package["digest"] + '"',
                "Content-Disposition": 'attachment; filename="' + package["filename"] + '"',
                "Content-Security-Policy": "default-src 'none'; sandbox",
            },
        )

    @app.get("/v1/tenants/{tenant}/retention-schedule")
    def retention_schedule(request: Request, tenant: str):
        return service.privacy.retention_schedule(auth.resolve(request), uuid(tenant))

    # Denial auditing, tenant retention policies and retention holds (v0.27): explicit routes before
    # the generic handlers.
    @app.get("/v1/tenants/{tenant}/access-denials")
    def access_denials(request: Request, tenant: str, limit: int = 50, since: str | None = None):
        return security_events.listing(db, auth.resolve(request), uuid(tenant), limit, since)

    @app.get("/v1/tenants/{tenant}/retention-policies")
    def retention_policy_list(request: Request, tenant: str, limit: int = 50, cursor: str | None = None):
        return retention_policies.listing(auth.resolve(request), uuid(tenant), limit, cursor)

    @app.post("/v1/tenants/{tenant}/retention-policies", status_code=201)
    async def create_retention_policy(request: Request, tenant: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            retention_policies.create, auth.resolve(request), uuid(tenant), body, request.state.correlation
        )

    @app.get("/v1/tenants/{tenant}/retention-policies/{obj}")
    def retention_policy(request: Request, tenant: str, obj: str):
        return retention_policies.get(auth.resolve(request), uuid(tenant), uuid(obj))

    @app.patch("/v1/tenants/{tenant}/retention-policies/{obj}")
    async def patch_retention_policy(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            retention_policies.patch,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            body,
            request.state.correlation,
        )

    @app.post("/v1/tenants/{tenant}/retention-policies/{obj}/actions/approve")
    async def approve_retention_policy(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            retention_policies.approve,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            body,
            request.state.correlation,
        )

    @app.get("/v1/tenants/{tenant}/retention-holds")
    def retention_holds(request: Request, tenant: str, limit: int = 50):
        return retention_policies.holds(auth.resolve(request), uuid(tenant), limit)

    @app.post("/v1/tenants/{tenant}/retention-holds", status_code=201)
    async def place_retention_hold(request: Request, tenant: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            retention_policies.place, auth.resolve(request), uuid(tenant), body, request.state.correlation
        )

    @app.post("/v1/tenants/{tenant}/retention-holds/{obj}/actions/release")
    async def release_retention_hold(request: Request, tenant: str, obj: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            retention_policies.release,
            auth.resolve(request),
            uuid(tenant),
            uuid(obj),
            body,
            request.state.correlation,
        )

    @app.get("/v1/tenants/{tenant}/retention-proofs")
    def retention_proofs(request: Request, tenant: str):
        return service.privacy.retention_proofs(auth.resolve(request), uuid(tenant))

    @app.get("/v1/tenants/{tenant}/{route}")
    def listing(request: Request, tenant: str, route: str, limit: int = 50, cursor: str | None = None):
        if route in ADMIN_READS:
            return administration.listing(auth.resolve(request), uuid(tenant), route, limit, cursor)
        return service.listing(auth.resolve(request), uuid(tenant), route, limit, cursor)

    @app.get("/v1/tenants/{tenant}/{route}/{obj}")
    def get(request: Request, tenant: str, route: str, obj: str):
        return service.get(auth.resolve(request), uuid(tenant), route, uuid(obj))

    async def command(request, tenant, route, obj=None, action=None):
        body = await strict_body(request)

        def run():
            if request.method == "POST" and (route, action) in COMMANDS:
                result = administration.command(
                    auth.resolve(request),
                    uuid(tenant),
                    route,
                    body,
                    request.state.correlation,
                    uuid(obj) if obj else None,
                    action,
                )
                return JSONResponse(result, status_code=200)
            return service.command(
                auth.resolve(request),
                uuid(tenant),
                route,
                body,
                request.state.correlation,
                uuid(obj) if obj else None,
                action,
            )

        return await run_in_threadpool(run)

    # Audit export (v0.25 part A): an explicit route, registered before the generic create.
    @app.post("/v1/tenants/{tenant}/audit-exports")
    async def audit_export(request: Request, tenant: str):
        body = await strict_body(request)
        return await run_in_threadpool(
            lambda: audit_exports.create(auth.resolve(request), uuid(tenant), body, request.state.correlation)
        )

    @app.post("/v1/tenants/{tenant}/disclosure-requests")
    async def disclosure_request(request: Request, tenant: str):
        return await command(request, tenant, "disclosure-requests")

    @app.post("/v1/tenants/{tenant}/{route}", status_code=201)
    async def create(request: Request, tenant: str, route: str):
        return await command(request, tenant, route)

    @app.patch("/v1/tenants/{tenant}/{route}/{obj}")
    async def patch(request: Request, tenant: str, route: str, obj: str):
        return await command(request, tenant, route, obj)

    @app.post("/v1/tenants/{tenant}/{route}/{obj}/actions/{action}")
    async def action(request: Request, tenant: str, route: str, obj: str, action: str):
        return await command(request, tenant, route, obj, action)

    if (ROOT / "apps/web/dist/assets").exists():
        app.mount("/assets", StaticFiles(directory=ROOT / "apps/web/dist/assets"), name="assets")

    @app.get("/ai-walkthrough.html", include_in_schema=False)
    def fictional_ai_walkthrough():
        # Public static examples only: no identity, tenant, provider or DB access.
        target = ROOT / "apps/web/dist/ai-walkthrough.html"
        if not target.exists():
            return JSONResponse({"message": "Fictional walkthrough unavailable."}, 503)
        return FileResponse(
            target,
            headers={
                "Content-Security-Policy": (
                    "default-src 'none'; script-src 'self'; style-src 'self'; "
                    "style-src-attr 'unsafe-inline'; connect-src 'none'; img-src 'none'; "
                    "object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
                )
            },
        )

    @app.get("/")
    def index():
        target = ROOT / "apps/web/dist/index.html"
        if not target.exists():
            return JSONResponse({"message": "Build the web client using npm run build in apps/web."}, 503)
        return FileResponse(target)

    return app
