# Implementation Status

**Audit baseline:** repository inspection updated after Phase 5 Step 1 & Step 2 backend implementation.  
**Overall maturity:** Phase 5 backend foundation and delivery models implemented (customer, project, assignments, milestones, tasks, progress, overdue detection, security, and tests); views and financial/approval modules remain planned.

This document separates repository evidence from planned requirements. A feature should only be marked implemented after its code, access controls, and relevant tests have been reviewed.

## Confirmed implementation

| Component | Status | Evidence from repository audit |
|---|---|---|
| Odoo module metadata | Present | `projectops_core/__manifest__.py` |
| Python add-on package | Present | `projectops_core/__init__.py`, `projectops_core/models/__init__.py` |
| ProjectOps root menu | Present | `projectops_core/views/menu_views.xml` |
| Manifest dependencies | `base`, `mail`, `project` | `projectops_core/__manifest__.py` |
| Customer & Project models | Implemented (backend) | `projectops_core/models/res_partner.py`, `projectops_core/models/project_project.py` |
| Project assignments | Implemented (backend) | `projectops_core/models/project_assignment.py` (`projectops.assignment`) |
| Milestones | Implemented (backend) | `projectops_core/models/project_milestone.py` (`projectops.milestone`) |
| Tasks, progress & overdue | Implemented (backend) | `projectops_core/models/project_task.py` (`project.task`), `project_project.py` |
| Security & access rules | Implemented (Step 1–2) | `projectops_core/security/projectops_security.xml`, `ir.model.access.csv` |
| Automated tests | Implemented (Step 1–2) | `projectops_core/tests/` (34 tests passing in `projectops_dev`) |

## Feature status

| Feature area | Status | What is missing |
|---|---|---|
| Customer management | Backend implemented | Custom ProjectOps customer views/actions |
| Project management | Backend implemented | Custom ProjectOps project views/actions; financial/cost fields |
| Tasks and milestones | Backend implemented | Custom ProjectOps task/milestone views/actions |
| Team assignments | Backend implemented | Assignment views/UI integration |
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
| Security and permissions | Implemented (Step 1–2) | Rules for worklogs, expenses, approvals, billing, and payments |
| Automated tests | Implemented (Step 1–2) | Tests for worklogs, expenses, approvals, costs, billing, and UI |

## Repository components not found during the audit

The `data/`, `report/`, `wizard/`, `controllers/`, `static/`, and `i18n/` directories are not yet present and will be added as their features are implemented.

The audit also found no repository-defined Docker setup, CI workflow, or Python dependency manifest (local Odoo 19 testing uses `odoo.conf` and `projectops_dev`).

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
