# Impact Platform application image: the API (serving the compiled web client), the outbox worker,
# the database preparation job and the operator bootstrap all run from this one image.
# Build from the repository root:  docker build -f deploy/Dockerfile -t impact-platform:<commit> .

# ---- Stage 1: compile the React client -----------------------------------------------------
FROM node:24-bookworm-slim AS web
WORKDIR /src/apps/web
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY apps/web/ ./
RUN npm run build

# ---- Stage 2: Python runtime ---------------------------------------------------------------
FROM python:3.12-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/apps/api
# Every distribution is pinned by version and SHA-256 (deploy/requirements.runtime.txt is generated
# from requirements.lock by deploy/hash_requirements.py); wheels only, nothing compiled here.
COPY deploy/requirements.runtime.txt /tmp/requirements.runtime.txt
RUN pip install --no-cache-dir --require-hashes --only-binary=:all: -r /tmp/requirements.runtime.txt \
    && rm /tmp/requirements.runtime.txt \
    && useradd --system --uid 10001 --user-group --home-dir /app --shell /usr/sbin/nologin impact
WORKDIR /app
# Only what the processes read at run time: the version source, the API package, the generated contracts, the two
# specification files the contract loader reads, the migrations and the operational scripts.
COPY VERSION.json VERSION.json
COPY apps/api/impact_api apps/api/impact_api
COPY packages/contracts packages/contracts
COPY specification/contracts/entity-catalogue.json specification/contracts/entity-catalogue.json
COPY specification/database/reference-map.json specification/database/reference-map.json
COPY infrastructure/migrations infrastructure/migrations
COPY scripts/migrate.py scripts/provision_logins.py scripts/fixture_support.py scripts/bootstrap_operator.py scripts/smoke.py scripts/
COPY deploy/prepare_database.py deploy/keycloak_admin.py deploy/mail_sink.py deploy/
COPY --from=web /src/apps/web/dist apps/web/dist
RUN mkdir -p /var/lib/impact/mail && chown impact:impact /var/lib/impact/mail
USER impact
EXPOSE 8000
# The API. The worker, the database job and the bootstrap override the command (deploy/compose.yaml).
CMD ["python", "-m", "uvicorn", "impact_api.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*", "--no-server-header", "--no-access-log"]
