# Implementation Status

**Audit baseline:** repository inspection supplied by the project team.  
**Overall maturity:** pre-implementation / add-on skeleton.

This document separates repository evidence from planned requirements. A feature should only be marked implemented after its code, access controls, and relevant tests have been reviewed.

## Confirmed implementation

| Component | Status | Evidence from repository audit |
|---|---|---|
| Odoo module metadata | Present | `projectops_core/__manifest__.py` |
| Python add-on package | Present, minimal | `projectops_core/__init__.py` |
| ProjectOps root menu | Present | `projectops_core/views/menu_views.xml` |
| Manifest dependency | `base` only | `projectops_core/__manifest__.py` |
| Loaded XML data | Menu XML only | Manifest data declaration |

## Feature status

| Feature area | Status | What is missing |
|---|---|---|
| Customer management | Planned | No custom model, inherited model, action, or view |
| Project management | Planned | No project extension or custom project model |
| Tasks and milestones | Planned | No task/milestone implementation |
| Team assignments | Planned | No assignment model or membership logic |
| Worklogs | Planned | No worklog model or submission flow |
| Worklog approvals | Planned | No approval states, methods, or approval history |
| Expenses | Planned | No expense extension or custom expense workflow |
| Expense approvals | Planned | No approval logic or authorization checks |
| Cost calculations | Planned | No cost fields or calculation methods |
| Budget utilization | Planned | No budget fields or utilization calculation |
| Billing records | Planned | No project billing implementation |
| Payment tracking | Planned | No project payment or balance logic |
| Dashboards | Planned | No dashboard or analytical views |
| Project health | Planned | No health field, thresholds, or display |
| PDF reports | Planned | No QWeb report template or report action |
| Security and permissions | Not implemented | No groups, access CSV, record rules, or model checks |
| Automated tests | Not implemented | No test package or test cases |

## Repository components not found during the audit

The audit did not find custom `models/`, `security/`, `data/`, `report/`, `tests/`, `wizard/`, `controllers/`, `static/`, or `i18n/` directories. These may be added as implementation proceeds.

The audit also found no repository-defined Docker setup, Odoo configuration, Python dependency manifest, CI workflow, or documented test command.

## Important implementation rules for future updates

- Do not mark a feature implemented based only on a requirements or architecture document.
- Confirm both UI behavior and server-side model behavior.
- For sensitive records, verify access rights and record rules; hiding a menu or button is not sufficient.
- Add automated tests for approval authority, financial calculations, and access boundaries.
- Update this table when code and tests materially change.
- Keep planned model names and relationships labeled as proposals until fit-gap decisions are approved.

## Known open decisions

The project documentation still identifies decisions to finalize, including the native-versus-custom model mapping, required Odoo apps, role permissions, approval authority, rejection and resubmission behavior, corrections and reversals, payment overpayments/refunds, currency rounding, project completion, and project-health thresholds.

[Back to documentation index](README.md)
