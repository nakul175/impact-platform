"""Performance measurement harness (QA 2026-10): measurement, not claims.

Run only through `scripts/perf.py` (`make perf`), which provisions a native PostgreSQL database with
the four login roles, starts the API on them exactly as `scripts/run.py test --native` does and then
runs this file with IMPACT_PERF=1. The file name does not match `test_*.py`, so the ordinary suites
never collect it.

Every object is created through the governed API (no direct inserts), so the seed itself exercises
the save and approval paths, and every timed request is the client-observed wall time of one HTTP
request on loopback (no browser rendering). The synthetic workload, its scale and its deterministic
values come from `perf_support.py`; the raw samples and their summaries are written to the JSON
named by IMPACT_PERF_OUTPUT."""

import asyncio
import json
import os
import platform
import random
import threading
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone

import httpx
import pytest

from perf_support import (
    MIX,
    TARGETS,
    import_csv,
    profile,
    ratio_values,
    summarize,
    verdict,
    windows,
    workload,
)
from test_calculation_methods import observation_data
from test_dashboards import RATIO
from test_forms import planned, workflow_version
from test_import import HOUSEHOLDS, batch_data, commit_body
from test_live_application import cmd
from test_measurement import get
from test_measurement_unit import definition
from test_period_governance import request_close
from test_publication import approved_report
from test_report_exports import FORMATS
from test_worker import make_worker
from impact_api.worker import empty_summary

pytestmark = pytest.mark.skipif(os.environ.get("IMPACT_PERF") != "1", reason="Run through scripts/perf.py")


def hardware():
    mem = None
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemTotal:"):
                mem = round(int(line.split()[1]) / 1024 / 1024, 1)
    except OSError:
        pass
    return {
        "cpu_count": os.cpu_count(),
        "memory_gib": mem,
        "machine": platform.machine(),
        "kernel": platform.release(),
        "python": platform.python_version(),
    }


class Probe:
    """Collects per-class latency samples (ms), error counts and a few error examples."""

    def __init__(self, live):
        self.live = live
        self.samples = defaultdict(list)
        self.stamped = defaultdict(list)
        self.started = time.perf_counter()
        self.errors = defaultdict(int)
        self.examples = defaultdict(list)
        self.scenarios = {}
        self.lock = threading.Lock()

    def _record(self, name, ms, response, ok):
        with self.lock:
            if response is not None and response.status_code in ok:
                self.samples[name].append(ms)
                self.stamped[name].append((time.perf_counter() - self.started, ms))
                return
            self.errors[name] += 1
            if len(self.examples[name]) < 3:
                self.examples[name].append(
                    "exception" if response is None else f"{response.status_code} {response.text[:200]}"
                )

    def sync(self, name, method, path, actor="author", body=None, ok=(200, 201)):
        started = time.perf_counter()
        try:
            response = self.live.request(path, actor=actor, method=method, body=body)
        except httpx.HTTPError:
            response = None
        self._record(name, (time.perf_counter() - started) * 1000, response, ok)
        if response is None or response.status_code not in ok:
            raise AssertionError(f"{name}: {self.examples[name][-1]}")
        return response.json()

    async def call(self, client, name, method, path, actor="author", body=None, ok=(200, 201)):
        headers = {"Authorization": "Bearer " + self.live.token(actor)}
        started = time.perf_counter()
        try:
            response = await client.request(method, path, json=body, headers=headers)
        except httpx.HTTPError:
            response = None
        self._record(name, (time.perf_counter() - started) * 1000, response, ok)
        return response if response is not None and response.status_code in ok else None

    def scenario(self, name, started, **facts):
        self.scenarios[name] = {
            "wall_seconds": round(time.perf_counter() - started, 2),
            "loadavg_after": [round(x, 2) for x in os.getloadavg()],
            **facts,
        }


async def bounded(concurrency, jobs):
    """Run coroutine factories with at most `concurrency` in flight."""
    gate = asyncio.Semaphore(concurrency)

    async def one(job):
        async with gate:
            return await job()

    return await asyncio.gather(*(one(j) for j in jobs))


def client(live):
    return httpx.AsyncClient(
        base_url=os.environ["IMPACT_BASE_URL"],
        trust_env=False,
        timeout=60,
        limits=httpx.Limits(max_connections=32),
    )


# -- governed seed (timed: every create is a save, every approve an approval) ------------------


def create(probe, route, data, name="write.save"):
    receipt = probe.sync(name, "POST", probe.live.path(route), body=cmd(data))
    return probe.sync("read.record", "GET", probe.live.path(route, receipt["object_id"]))


def act(probe, route, row, verb, data=None, actor="author", name="write.save"):
    return probe.sync(
        name,
        "POST",
        probe.live.path(route, row["object_id"]) + "/actions/" + verb,
        actor=actor,
        body=cmd(data or {}, row["revision_id"]),
    )


def review(probe, route, row, wf):
    receipt = act(probe, route, row, "submit", {"workflow_version": wf})
    workflow = probe.sync("read.record", "GET", probe.live.path("workflows", receipt["object_id"]))
    act(
        probe,
        "workflows",
        workflow,
        "approve",
        {
            "candidate_revision": workflow["data"]["candidate_revision"],
            "reason": "Synthetic performance workload: verified.",
        },
        actor="reviewer",
        name="write.approval",
    )


def seed_programme(
    probe, w, index, wf, period, calendar, geography, indicators=None, obligations=None, observe=True
):
    """One active programme of `indicators` ratio indicators, each with an approved plan of
    `obligations` MANUAL sources; with `observe`, one approved observation per obligation
    (sequential). Returns (programme, [(indicator, keys)])."""
    live = probe.live
    n_indicators = w.indicators if indicators is None else indicators
    n_obligations = w.obligations if obligations is None else obligations
    programme = create(
        probe,
        "programmes",
        {
            "code": "PRF",
            "title": f"Performance {index} " + str(uuid.uuid4())[:8],
            "programme_type": "Health",
            "starts_at": "2026-01-01T00:00:00Z",
            "ends_at": "2027-01-01T00:00:00Z",
            "reporting_calendar_id": calendar,
            "geography_id": geography,
        },
    )
    values = iter(ratio_values(w.seed + index, n_indicators * n_obligations))
    indicators = []
    for i in range(n_indicators):
        d = create(probe, "indicator-definitions", definition(**RATIO, name=f"Synthetic ratio {index}.{i}"))
        review(probe, "indicator-definitions", d, wf)
        d = get(live, "indicator-definitions", d["object_id"])
        indicator = create(
            probe,
            "indicator-instances",
            {
                "programme_id": programme["object_id"],
                "definition_version": d["revision_id"],
                "local_applicability": "Synthetic households",
                "collector_id": live.fixture["actors"]["author"]["principal_id"],
                "reviewer_id": live.fixture["actors"]["reviewer"]["principal_id"],
            },
        )
        keys = [str(uuid.uuid4()) for _ in range(n_obligations)]
        plan = create(
            probe,
            "collection-plans",
            {
                "title": "Synthetic collection",
                "indicator_id": indicator["object_id"],
                "period_id": period["object_id"],
                "obligations": [
                    {
                        "label": f"Site {k + 1}",
                        "source_namespace": "MANUAL",
                        "source_key": key,
                        "due_at": "2026-09-01T00:00:00Z",
                    }
                    for k, key in enumerate(keys)
                ],
            },
        )
        review(probe, "collection-plans", plan, wf)
        act(probe, "indicator-instances", indicator, "activate")
        indicators.append((get(live, "indicator-instances", indicator["object_id"]), keys))
    act(probe, "programmes", programme, "ready")
    act(probe, "programmes", get(live, "programmes", programme["object_id"]), "activate")
    for indicator, keys in indicators if observe else []:
        for key in keys:
            n, d = next(values)
            row = create(
                probe,
                "observations",
                observation_data(indicator, key, "0", {}) | {"numerator": n, "denominator": d},
            )
            review(probe, "observations", row, wf)
    return get(live, "programmes", programme["object_id"]), indicators


async def observe_concurrently(probe, w, indicator, keys, wf):
    """Create, submit and independently approve one ratio observation per key at concurrency C:
    POST create and POST submit are saves, POST approve an approval, each GET a record read."""
    live = probe.live
    values = ratio_values(w.seed + 9999, len(keys))
    async with client(live) as http:

        async def one(key, n, d):
            r = await probe.call(
                http,
                "write.save",
                "POST",
                live.path("observations"),
                body=cmd(observation_data(indicator, key, "0", {}) | {"numerator": n, "denominator": d}),
            )
            if r is None:
                return
            r = await probe.call(http, "read.record", "GET", live.path("observations", r.json()["object_id"]))
            if r is None:
                return
            row = r.json()
            r = await probe.call(
                http,
                "write.save",
                "POST",
                live.path("observations", row["object_id"]) + "/actions/submit",
                body=cmd({"workflow_version": wf}, row["revision_id"]),
            )
            if r is None:
                return
            r = await probe.call(http, "read.record", "GET", live.path("workflows", r.json()["object_id"]))
            if r is None:
                return
            wfl = r.json()
            await probe.call(
                http,
                "write.approval",
                "POST",
                live.path("workflows", wfl["object_id"]) + "/actions/approve",
                actor="reviewer",
                body=cmd(
                    {
                        "candidate_revision": wfl["data"]["candidate_revision"],
                        "reason": "Synthetic performance workload: verified.",
                    },
                    wfl["revision_id"],
                ),
            )

        await bounded(w.concurrency, [lambda k=k, v=v: one(k, *v) for k, v in zip(keys, values)])


def calculate(probe, indicator, period, name="calculate.indicator"):
    receipt = act(
        probe, "indicator-instances", indicator, "calculate", {"period_id": period["object_id"]}, name=name
    )
    return get(probe.live, "calculated-results", receipt["object_id"])


def dashboard_path(live, programme, period):
    return live.path("programmes", programme["object_id"]) + "/dashboard?period_id=" + period["object_id"]


# -- closed-loop profiles (peak, soak, cohorts) ------------------------------------------------------


async def closed_loop(probe, w, prof, programmes, period, wf, deadline, concurrency, prefix=""):
    """`concurrency` virtual users each loop over the weighted mix until `deadline`: 100-row
    observation lists, indicator-instance record reads, warm dashboard reads and governed write
    cycles (create, read, submit, read workflow, independent approval). Class names are the base
    workload's, so the FSD verdicts apply unchanged; `prefix` separates a tenant cohort."""
    live = probe.live
    indicators = [i for _, inds in programmes for i in inds]
    ops = [name for name, weight in MIX.items() for _ in range(weight)]
    counter = {"iterations": 0}

    async def user(number):
        rng = random.Random(w.seed * 1000 + number)
        values = iter(ratio_values(w.seed + 5000 + number, 100000))
        async with client(live) as http:
            while time.perf_counter() < deadline:
                op = ops[rng.randrange(len(ops))]
                ind = indicators[rng.randrange(len(indicators))]
                counter["iterations"] += 1
                if op == "read.list100":
                    await probe.call(http, prefix + op, "GET", live.path("observations") + "?limit=100")
                elif op == "read.record":
                    await probe.call(
                        http, prefix + op, "GET", live.path("indicator-instances", ind["object_id"])
                    )
                elif op == "dashboard.warm":
                    programme = programmes[rng.randrange(len(programmes))][0]
                    await probe.call(http, prefix + op, "GET", dashboard_path(live, programme, period))
                else:
                    n, d = next(values)
                    r = await probe.call(
                        http,
                        prefix + "write.save",
                        "POST",
                        live.path("observations"),
                        body=cmd(
                            observation_data(ind, str(uuid.uuid4()), "0", {})
                            | {"numerator": n, "denominator": d}
                        ),
                    )
                    if r is None:
                        continue
                    r = await probe.call(
                        http, prefix + "read.record", "GET", live.path("observations", r.json()["object_id"])
                    )
                    if r is None:
                        continue
                    row = r.json()
                    r = await probe.call(
                        http,
                        prefix + "write.save",
                        "POST",
                        live.path("observations", row["object_id"]) + "/actions/submit",
                        body=cmd({"workflow_version": wf}, row["revision_id"]),
                    )
                    if r is None:
                        continue
                    r = await probe.call(
                        http, prefix + "read.record", "GET", live.path("workflows", r.json()["object_id"])
                    )
                    if r is None:
                        continue
                    wfl = r.json()
                    await probe.call(
                        http,
                        prefix + "write.approval",
                        "POST",
                        live.path("workflows", wfl["object_id"]) + "/actions/approve",
                        actor="reviewer",
                        body=cmd(
                            {
                                "candidate_revision": wfl["data"]["candidate_revision"],
                                "reason": "Synthetic performance workload: verified.",
                            },
                            wfl["revision_id"],
                        ),
                    )

    await asyncio.gather(*(user(n) for n in range(concurrency)))
    return counter["iterations"]


async def quiet_reader(probe, name, path, actor, deadline):
    """One quiet tenant's reader at concurrency 1 until `deadline` (the cohort probe)."""
    live = probe.live
    async with client(live) as http:
        while time.perf_counter() < deadline:
            await probe.call(http, name, "GET", path, actor=actor)


def third_tenant(live):
    """A freshly onboarded, Active managed tenant whose owner is the fixture author (the control
    plane's own bootstrap path); returns (tenant_id, a read path that answers 200 for the owner)."""
    from test_authority_renewal import bootstrapped_tenant

    tenant, _ = bootstrapped_tenant(live)
    tenant_id = tenant["tenant_id"]
    for route in ["programmes?limit=100", "me/access"]:
        path = live.path(route, tenant=tenant_id)
        if live.request(path).status_code == 200:
            return tenant_id, path
    raise AssertionError("the onboarded tenant's owner cannot read it")


def run_profile(probe, w, prof, programmes, period, wf):
    """The closed-loop phase of a non-base profile; returns the scenario facts."""
    live = probe.live
    concurrency = prof.concurrency(w.concurrency)
    facts = {"profile": prof.describe(), "concurrency": concurrency}
    if prof.name == "cohorts":
        tenant_b = live.fixture["tenant_b"]
        path_b = live.path("programmes", tenant=tenant_b) + "?limit=100"
        tenant_c, path_c = third_tenant(live)
        facts["tenant_c"] = tenant_c

        async def idle():
            deadline = time.perf_counter() + max(10, prof.duration // 6)
            await asyncio.gather(
                quiet_reader(probe, "isolation.tenant_b.idle", path_b, "other_tenant", deadline),
                quiet_reader(probe, "isolation.tenant_c.idle", path_c, "author", deadline),
            )

        async def noisy():
            deadline = time.perf_counter() + prof.duration
            iterations, *_ = await asyncio.gather(
                closed_loop(probe, w, prof, programmes, period, wf, deadline, concurrency),
                quiet_reader(probe, "isolation.tenant_b.during_cohorts", path_b, "other_tenant", deadline),
                quiet_reader(probe, "isolation.tenant_c.during_cohorts", path_c, "author", deadline),
            )
            return iterations

        asyncio.run(idle())
        facts["noisy_iterations"] = asyncio.run(noisy())
        for name in ["isolation.tenant_b", "isolation.tenant_c"]:
            idle_p95 = summarize(probe.samples[name + ".idle"])["p95_ms"]
            busy_p95 = summarize(probe.samples[name + ".during_cohorts"])["p95_ms"]
            facts[name + "_p95_ratio"] = round(busy_p95 / idle_p95, 2) if idle_p95 and busy_p95 else None
        return facts
    deadline = time.perf_counter() + prof.duration
    facts["iterations"] = asyncio.run(
        closed_loop(probe, w, prof, programmes, period, wf, deadline, concurrency)
    )
    facts["windows"] = {
        name: windows(probe.stamped[name], prof.window)
        for name in ["read.list100", "read.record", "dashboard.warm", "write.save", "write.approval"]
    }
    return facts


# -- the measured run ----------------------------------------------------------------------------


def test_performance_workload(live):
    w = workload(
        os.environ.get("IMPACT_PERF_SCALE", "sandbox"),
        int(os.environ.get("IMPACT_PERF_SEED", "20261001")),
        int(os.environ.get("IMPACT_PERF_CONCURRENCY", "4")),
    )
    probe = Probe(live)
    started_at = datetime.now(timezone.utc).isoformat()
    loadavg_before = [round(x, 2) for x in os.getloadavg()]
    with live.db() as c:
        server_version = c.execute("SELECT version() AS v").fetchone()["v"]
        settings = {
            r["name"]: r["setting"]
            for r in c.execute(
                "SELECT name, setting FROM pg_settings WHERE name IN "
                "('shared_buffers','work_mem','max_connections','synchronous_commit','fsync')"
            ).fetchall()
        }
    wf = workflow_version(live)
    period = get(live, "periods", live.records["period"]["object_id"])
    calendar = get(live, "reporting-calendars")["items"][0]["object_id"]
    geography = get(live, "geographies")["items"][0]["object_id"]

    # 1. Seed P programmes x I ratio indicators x K approved manual observations (concurrency 1).
    t = time.perf_counter()
    programmes = [
        (p, [i for i, _ in inds])
        for p, inds in (
            seed_programme(probe, w, n, wf, period, calendar, geography) for n in range(w.programmes)
        )
    ]
    probe.scenario(
        "seed",
        t,
        concurrency=1,
        programmes=w.programmes,
        indicators=w.programmes * w.indicators,
        observations=w.manual_observations,
    )

    # 2. Provisional calculation of every indicator, then a cold dashboard read per programme
    #    (the first read after new results; the build has no dashboard cache, so "cold" and
    #    "warm" differ only by database and connection state).
    t = time.perf_counter()
    for programme, indicators in programmes:
        for indicator in indicators:
            calculate(probe, indicator, period)
        probe.sync("dashboard.cold", "GET", dashboard_path(live, programme, period))
    probe.scenario("calculate_and_cold_dashboard", t, concurrency=1)

    prof = profile(
        os.environ.get("IMPACT_PERF_PROFILE", "base"),
        int(os.environ["IMPACT_PERF_DURATION"]) if os.environ.get("IMPACT_PERF_DURATION") else None,
    )
    if prof.name != "base":
        t = time.perf_counter()
        facts = run_profile(probe, w, prof, programmes, period, wf)
        probe.scenario("profile_" + prof.name, t, **facts)
        return finish(probe, w, prof, started_at, loadavg_before, server_version, settings)

    tenant_b = live.fixture["tenant_b"]
    tenant_b_read = live.path("programmes", tenant=tenant_b) + "?limit=100"

    async def interactive():
        async with client(live) as http:
            # Tenant B baseline before tenant A's large work (VF-CAP-002 isolation probe).
            await bounded(
                1,
                [
                    lambda: probe.call(
                        http, "isolation.tenant_b.idle", "GET", tenant_b_read, actor="other_tenant"
                    )
                    for _ in range(40)
                ],
            )
            some = [o for _, inds in programmes for o in inds]
            obs = live.path("observations") + "?limit=100"
            jobs = []
            for i in range(w.read_samples):
                ind = some[i % len(some)]
                jobs += [
                    lambda: probe.call(http, "read.list100", "GET", obs),
                    lambda: probe.call(http, "read.list100", "GET", live.path("programmes") + "?limit=100"),
                    lambda ind=ind: probe.call(
                        http, "read.record", "GET", live.path("indicator-instances", ind["object_id"])
                    ),
                ]
            for i in range(max(20, w.read_samples // 4)):
                programme = programmes[i % len(programmes)][0]
                jobs.append(
                    lambda p=programme: probe.call(
                        http, "dashboard.warm", "GET", dashboard_path(live, p, period)
                    )
                )
            await bounded(w.concurrency, jobs)

    t = time.perf_counter()
    asyncio.run(interactive())
    probe.scenario("interactive_reads", t, concurrency=w.concurrency, requests_per_class=w.read_samples)

    # 3. Maximum bounded import batch (500 rows x 1 value column = 500 observations), while tenant B
    #    reads continuously at concurrency 1.
    indicator, period_i, _ = planned(live, **HOUSEHOLDS)
    content = import_csv(w.seed, w.import_rows, "P" + str(uuid.uuid4())[:6])
    import_phases = {}
    done = threading.Event()

    def run_import():
        try:
            batch = create(probe, "imports", batch_data(indicator, period_i, content), name="import.create")
            tt = time.perf_counter()
            probe.sync(
                "import.preview",
                "POST",
                live.path("imports", batch["object_id"]) + "/actions/preview",
                body=cmd({}, batch["revision_id"]),
            )
            import_phases["preview_ms"] = round((time.perf_counter() - tt) * 1000, 1)
            staged = get(live, "imports", batch["object_id"])
            import_phases["preview_counts"] = staged["data"]["preview"]["counts"]
            tt = time.perf_counter()
            probe.sync(
                "import.commit",
                "POST",
                live.path("imports", batch["object_id"]) + "/actions/commit",
                body=commit_body(staged, wf=wf),
            )
            import_phases["commit_ms"] = round((time.perf_counter() - tt) * 1000, 1)
            import_phases["observation_ids"] = get(live, "imports", batch["object_id"])["data"]["committed"][
                "observation_ids"
            ]
        finally:
            done.set()

    async def isolation_during(name):
        async with client(live) as http:
            while not done.is_set():
                await probe.call(http, name, "GET", tenant_b_read, actor="other_tenant")

    t = time.perf_counter()
    worker_thread = threading.Thread(target=run_import)
    worker_thread.start()
    asyncio.run(isolation_during("isolation.tenant_b.during_import"))
    worker_thread.join()
    imported = import_phases.pop("observation_ids", [])
    probe.scenario("import_max_batch", t, rows=w.import_rows, observations=len(imported), **import_phases)

    # 4. Independent approval of every imported observation at concurrency C (GET workflow is a
    #    record read; POST approve is an approval), tenant B still reading.
    with live.db() as c:
        rows = c.execute(
            "SELECT r.object_id::text AS w, v.payload->>'candidate_id' AS o FROM impact.object_registry r "
            "JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
            "WHERE r.object_type='Workflow' AND v.payload->>'candidate_id' = ANY(%s)",
            (imported,),
        ).fetchall()
    workflows = [r["w"] for r in rows]

    async def approvals():
        async with client(live) as http:

            async def approve_one(wid):
                r = await probe.call(http, "read.record", "GET", live.path("workflows", wid))
                if r is None:
                    return
                wfl = r.json()
                await probe.call(
                    http,
                    "write.approval",
                    "POST",
                    live.path("workflows", wid) + "/actions/approve",
                    actor="reviewer",
                    body=cmd(
                        {
                            "candidate_revision": wfl["data"]["candidate_revision"],
                            "reason": "Synthetic performance workload: verified.",
                        },
                        wfl["revision_id"],
                    ),
                )

            async def tenant_b():
                while not finished.is_set():
                    await probe.call(
                        http,
                        "isolation.tenant_b.during_approvals",
                        "GET",
                        tenant_b_read,
                        actor="other_tenant",
                    )

            finished = asyncio.Event()
            reader = asyncio.create_task(tenant_b())
            await bounded(w.concurrency, [lambda wid=wid: approve_one(wid) for wid in workflows])
            finished.set()
            await reader

    t = time.perf_counter()
    asyncio.run(approvals())
    probe.scenario("approve_imported", t, concurrency=w.concurrency, workflows=len(workflows))

    # 5. Calculation over a large approved observation set: one ratio indicator whose approved plan
    #    names the maximum 500 obligations, every source created, submitted and independently
    #    approved through the API at concurrency C, then calculated 5 times.
    t = time.perf_counter()
    large_programme, [(large_indicator, large_keys)] = seed_programme(
        probe, w, 900, wf, period, calendar, geography, indicators=1, obligations=w.import_rows, observe=False
    )
    asyncio.run(observe_concurrently(probe, w, large_indicator, large_keys, wf))
    probe.scenario("seed_large", t, concurrency=w.concurrency, observations=len(large_keys))
    t = time.perf_counter()
    large = None
    for _ in range(5):
        large = calculate(
            probe,
            get(live, "indicator-instances", large_indicator["object_id"]),
            period,
            name="calculate.large",
        )
    data = (large or {}).get("data", {})
    probe.scenario(
        "calculate_large",
        t,
        value=data.get("value"),
        numerator=data.get("numerator"),
        denominator=data.get("denominator"),
        reason_code=data.get("reason_code"),
    )

    # 6. Freshness: a new approved source, recalculation, then poll the dashboard until the card
    #    shows the new result revision; measured from calculation completion (VF-PER-006). Run on
    #    the import programme, which is never closed (an unplanned source would block a close).
    t = time.perf_counter()
    fresh_programme = {"object_id": indicator["data"]["programme_id"]}
    for k in range(20):
        ind = get(live, "indicator-instances", indicator["object_id"])
        row = create(probe, "observations", observation_data(ind, str(uuid.uuid4()), str(k + 1), {}))
        review(probe, "observations", row, wf)
        result = calculate(probe, get(live, "indicator-instances", indicator["object_id"]), period_i)
        t0 = time.perf_counter()
        while time.perf_counter() - t0 < 120:
            body = probe.sync("dashboard.poll", "GET", dashboard_path(live, fresh_programme, period_i))
            card = next(c for c in body["indicators"] if c["indicator_id"] == ind["object_id"])
            if (card.get("provisional") or {}).get("result_revision") == result["revision_id"]:
                probe.samples["freshness.propagation"].append((time.perf_counter() - t0) * 1000)
                break
        else:
            probe.errors["freshness.propagation"] += 1
    probe.scenario("freshness", t)

    # 7. Period close per programme: request (preview + workflow) and independent approval (lock).
    t = time.perf_counter()
    closes = []
    for programme, indicators in programmes + [(large_programme, [large_indicator])]:
        for ind in indicators:
            calculate(probe, get(live, "indicator-instances", ind["object_id"]), period)
        try:
            tt = time.perf_counter()
            workflow = request_close(live, programme, period)
            requested = (time.perf_counter() - tt) * 1000
            tt = time.perf_counter()
            act(
                probe,
                "workflows",
                workflow,
                "approve",
                {
                    "candidate_revision": workflow["data"]["candidate_revision"],
                    "reason": "Synthetic performance workload: verified.",
                },
                actor="reviewer",
                name="period.close.approve",
            )
            probe.samples["period.close.request"].append(requested)
            closes.append(
                {
                    "indicators": len(indicators),
                    "request_ms": round(requested, 1),
                    "approve_ms": round((time.perf_counter() - tt) * 1000, 1),
                }
            )
        except AssertionError as e:
            probe.errors["period.close.request"] += 1
            probe.examples["period.close.request"].append(str(e)[:600])
    probe.scenario("period_close", t, closes=closes)

    # 8. Report export: acknowledgement of the request, then the worker's render of each format of
    #    the fixture report package (no queue wait: the in-process worker drains at once).
    t = time.perf_counter()
    worker = make_worker(live)
    tenant = live.fixture["tenant_a"]
    for _ in range(3):
        report = approved_report(live)
        for fmt in FORMATS:
            probe.sync(
                "export.acknowledge",
                "POST",
                live.path("reports", report["object_id"]) + "/actions/export",
                body=cmd({"format": fmt}, report["revision_id"]),
            )
        summary = empty_summary()
        for _ in range(10):
            claimed = worker.claim_exports(tenant, summary)
            if not claimed:
                break
            for row in claimed:
                tt = time.perf_counter()
                worker.process_export(tenant, row, summary)
                probe.samples["export.render"].append((time.perf_counter() - tt) * 1000)
    probe.scenario("report_export", t, formats=list(FORMATS), repetitions=3)

    finish(probe, w, prof, started_at, loadavg_before, server_version, settings)


def finish(probe, w, prof, started_at, loadavg_before, server_version, settings):
    classes = {}
    for name in sorted(set(probe.samples) | set(probe.errors)):
        s = summarize(probe.samples[name], probe.errors.get(name, 0))
        target = TARGETS.get(name)
        classes[name] = {
            **s,
            "requirement": target[0] if target else None,
            "target_p95_ms": target[1] if target else None,
            "target_p99_ms": target[2] if target else None,
            "verdict": verdict(name, s),
            "error_examples": probe.examples.get(name, []),
        }
    report = {
        "harness": "qualification/perf_harness.py via scripts/perf.py",
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "hardware": hardware(),
        "loadavg_before": loadavg_before,
        "database": {
            "server_version": server_version,
            "settings": settings,
            "topology": "single node, loopback, four provisioned login roles, "
            + (os.environ.get("IMPACT_DB_POOLER") or "no pooler"),
        },
        "api": {
            "base_url": os.environ["IMPACT_BASE_URL"],
            "workers": "one uvicorn process",
            "unprivileged_db": os.environ.get("IMPACT_REQUIRE_UNPRIVILEGED_DB") == "1",
        },
        "workload": w.describe(),
        "profile": prof.describe(),
        "scenarios": probe.scenarios,
        "classes": classes,
        "raw_ms": {k: [round(v, 2) for v in vs] for k, vs in probe.samples.items()},
    }
    out = os.environ.get("IMPACT_PERF_OUTPUT")
    if out:
        with open(out, "w") as f:
            json.dump(report, f, indent=2)
            f.write("\n")
    assert classes, "no measurements"
