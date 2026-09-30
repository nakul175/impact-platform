import json
import logging
from urllib.parse import parse_qs, urlparse
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
from .store import Database
from .tenant_lifecycle import TenantLifecycle
from .access_bootstrap import AccessBootstrap
from .authority_renewal import AuthorityRenewal
from .recovery_contacts import RecoveryContacts

LOG = logging.getLogger("impact")
MAX_BODY = 262144
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
    administration = Administration(s, db, service)
    lifecycle = TenantLifecycle(s, db)
    bootstrap_access = AccessBootstrap(lifecycle)
    authority_renewal = AuthorityRenewal(lifecycle)
    recovery_contacts = RecoveryContacts(lifecycle)
    app = FastAPI(title="Impact Platform", version="0.15.0", docs_url=None, redoc_url=None, openapi_url=None)
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
        supplied = request.headers.get("x-correlation-id", "")
        try:
            request.state.correlation = str(UUID(supplied))
        except ValueError:
            request.state.correlation = str(uuid4())
        host = request.headers.get("host", "").split(":")[0]
        if host not in {urlparse(s.public_origin).hostname, "testserver" if s.environment == "test" else ""}:
            response = error(request, DomainError("VALIDATION_FAILED", 400))
        elif (
            request.headers.get("content-length", "0").isdigit()
            and int(request.headers.get("content-length", "0")) > MAX_BODY
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
        if version != 17:
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

    @app.get("/v1/runtime-manifest")
    def manifest(request: Request):
        auth.resolve(request)
        return {
            "environment": s.environment,
            "build_id": "impact-0.15.0",
            "schema_version": "17",
            "api_version": "1.10.0",
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

    @app.get("/")
    def index():
        target = ROOT / "apps/web/dist/index.html"
        if not target.exists():
            return JSONResponse({"message": "Build the web client using npm run build in apps/web."}, 503)
        return FileResponse(target)

    return app
