# Release 0.60 coding candidate: role-based solution training

US-AD-01 / APL-355 (frozen Gherkin SHA-256 `e4796016a8e17310b2cb27944cf93509d908f86c45fddbc7d488000987c5f3a0`) adds learner-scoped Data Author training for one explicitly attested deployed solution. A completed deployment plan does not prove deployment. An authorised manager must first record the selected solution, deployment time and an accountable internal reference against the exact completed-plan revision.

The server owns the versioned role-to-module mapping. A current Data Author receives only the AUTHOR module set for the attested solution; modules assigned solely to reviewer or programme-manager roles are excluded. The runtime rechecks the current active role assignment, its active read grant and the plan scope before returning training or accepting completion.

Each completion is an immutable tenant-scoped record bound to the authenticated learner principal and membership, plan revision, deployment attestation, solution, role, module key and content version. The completion command uses an exact operation identity and plan revision. Repeating another operation for an already completed module returns the existing learner state without creating another completion. Completion records learning progress, not certification, approval or release acceptance.

Migration 0054 registers only the `AITrainingCompletion` object kind in the existing forced-RLS registry; it adds no table or runtime grant. All migrations 0001–0053 remain byte-exact.

This is a coding-only candidate. Contract generation, source parsing and type-oriented source checks are preparation; tests, CI, merge, staging deployment and owner acceptance remain deferred to the combined qualification phase.
