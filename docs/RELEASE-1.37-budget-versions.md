# Release 1.37 qualification candidate — versioned budgets

FR-FIN-002 / APL-648 adds budget versions by activity, category, partner, period and currency with explicit approval routes and exact-decimal totals. Every revision requires the exact current revision and retains original and current baseline comparisons.

Approval is restricted to a named approval-route principal who is a different natural person from every budget author. It pins the exact budget revision and rate assumptions. Budget changes keep actual expenditure independent and preserve historical variance. Retries enforce the exact payload and expiry.

Migration 0111 registers `BudgetVersion` behind restrictive worker fences. The focused disposable HTTP journey passed locally on 16 October 2026. CI, independent final review, merge, staging deployment and owner acceptance remain separate gates.
