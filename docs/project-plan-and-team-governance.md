# ProjectOps — Project Plan and Team Governance

## 1. Purpose and Guiding Principle

This document defines the roadmap, responsibilities, collaboration practices, checkpoints, deliverables, and risk controls for the four-member Keradion Technology internship team.

**Guiding principle:** ProjectOps is one integrated business system, not four independent features. Odoo is the platform; ProjectOps is the business solution. All components must share consistent data, business rules, permissions, and workflows.

## 2. Project Basis and Principles

| Item | Agreed information |
|---|---|
| Project | ProjectOps — Odoo-based project management and business operations system |
| Organization/context | Keradion Technology internship project |
| Team | Four members |
| Intended use | Initially internal to Keradion; designed to be reusable by other service businesses |
| Platform | Odoo 19 Community |
| Custom module | `projectops_core` |
| Collaboration | Shared GitHub repository |
| Database | PostgreSQL |

- Build ProjectOps as a custom Odoo add-on; reuse suitable Odoo capabilities and do not modify Odoo core or build an ERP from scratch.
- Connect project delivery and project-level financial information in one application.
- Only approved work hours and expenses contribute to recorded project cost.
- Project-health indicators are transparent warnings for management, not automatic decisions.
- A project can be operationally complete while customer payments remain outstanding.
- ProjectOps does not replace full accounting, payroll, HR, procurement, or inventory systems.
- Primary ownership is assigned by area; integration, peer review, and system-level decisions remain shared.

## 3. End-to-End Roadmap

The ten phases below provide the recommended lifecycle. Activities may overlap when dependencies are understood and agreed.

| Phase | Name | Main outcome |
|---|---|---|
| 0 | Initiation and team alignment | Agreed scope, Odoo 19 environment, repository workflow, responsibilities |
| 1 | Requirements and business analysis | Requirements, use cases, business rules, roles, acceptance criteria |
| 2 | Odoo investigation and fit-gap | Reuse/configure/extend/build decisions and module dependencies |
| 3 | System design and architecture | Reviewed data model, workflows, calculations, permissions, interfaces |
| 4 | Environment and module foundation | Working environment and installable `projectops_core` |
| 5 | Core implementation | Feature components, tests, incremental demonstrations |
| 6 | Integration | One connected application and end-to-end workflow |
| 7 | Testing and quality assurance | Test evidence, resolved defects, acceptance results |
| 8 | Deployment and documentation | Deployable module, guides, technical documentation, demo data |
| 9 | Demonstration and handover | Complete demonstration and agreed handover package |

### Phase activities and completion checks

**Phase 0 — Initiation and team alignment**
- Reconfirm proposal scope, intended users, and Odoo 19 version.
- Agree on development environment, database, GitHub branches, pull requests, reviews, communication, and blocker handling.
- Confirm primary responsibility areas and shared integration duties.
- **Outputs/check:** Scope and assumptions, working setup, repository process, and team agreement; every member understands the objective and responsibilities.

**Phase 1 — Requirements and business analysis**
- Identify actors and what each role can view/do.
- Describe the customer-to-project lifecycle and completion expectations.
- Define task, milestone, worklog, expense, approval, billing, and payment workflows.
- Document functional/non-functional requirements, business rules, validations, exceptions, status transitions, and acceptance criteria.
- **Outputs/check:** Requirements/backlog, use cases and process diagrams, rules, role/permission needs, and acceptance criteria; the team can explain each major workflow without undocumented assumptions.

**Phase 2 — Odoo investigation and fit-gap**
- Inspect Contacts, Project, Timesheets, Expenses, Accounting/Invoicing, reporting, users, and groups.
- Classify each requirement as reuse, configuration, extension, or custom implementation.
- Inspect models, relationships, views, security, and dependencies; verify required apps in the Odoo 19 environment.
- Record constraints and questions requiring team/supervisor decisions.
- **Outputs/check:** Investigation notes, fit-gap analysis, dependencies, and agreed implementation approach; every major custom component has a clear reason.

**Phase 3 — System design and architecture**
- Design conceptual/logical data models, ERD, fields, relationships, constraints, ownership, and record lifecycles.
- Identify reused/inherited Odoo models and required custom models.
- Define workflows and state transitions for projects, tasks, worklogs, expenses, and billing.
- Specify cost, budget utilization, outstanding balance, and project-health calculations.
- Define role-permission matrix and server-side access controls.
- Sketch screens, navigation, and reports; agree model/field names and shared interfaces before parallel work.
- **Outputs/check:** Architecture, ERD/data dictionary, workflow diagrams, calculation rules, permission matrix, UI sketches, and shared contracts; all members agree on the core design.

**Phase 4 — Environment and module foundation**
- Set up Odoo 19 and PostgreSQL; understand the addons directory and module loading.
- Create the `projectops_core` skeleton and manifest; configure initialization and basic navigation.
- Establish development/test databases and verify install, upgrade, and restart behavior.
- **Outputs/check:** Working environment, installable module, setup instructions, and shared database approach; all members can run it reliably.

**Phase 5 — Core implementation**
- Build customer/project registration, ownership, team assignment, dates, contract value, and cost budget.
- Build milestones, tasks, assignments, progress, and overdue detection.
- Build worklog/expense submission, receipt attachments, and status handling.
- Build approval/rejection, prevention of self-approval, and approval history.
- Calculate approved labour and expense costs, including historical hourly-rate snapshots.
- Build billing records, partial payments, balances, and overdue status.
- Build project/portfolio dashboards, documented metrics, explainable health indicators, and printable project summary.
- Add tests and security with each feature.
- **Outputs/check:** Working models, views, workflows, security, calculations, tests, and demonstrations; each component meets its acceptance criteria and is ready to integrate.

**Phase 6 — Integration**
- Merge reviewed pull requests; resolve model, field, relationship, and dependency mismatches.
- Connect approvals to cost calculations and project records; connect project, task, financial, and billing data to dashboards/reports.
- Recheck permissions across components and run complete scenarios with shared demo data.
- **Outputs/check:** Integrated module, resolved issues, end-to-end test evidence, updated technical documentation; users can complete the main workflow without manual data repair.

**Phase 7 — Testing and quality assurance**
- Test methods/calculations, constraints, relationships, validations, workflow transitions, approvals, and rejections.
- Test integration across project, worklog, expense, cost, billing, and reporting.
- Test each role with appropriately restricted accounts, including invalid inputs, missing values, and edge cases.
- Compare dashboard figures with independent hand calculations; run acceptance tests and record fixes.
- **Outputs/check:** Test plan/cases, automated and acceptance results, defect log, security evidence; critical workflows and permissions pass with no unresolved critical defect.

**Phase 8 — Deployment and documentation**
- Prepare a clean deployment environment; install the module and verify dependencies, configuration, roles, and permissions.
- Prepare fictional demonstration data.
- Write installation/setup instructions, user guide, technical documentation, and README.
- Verify another team member can reproduce installation from the documentation.
- **Outputs/check:** Deployable module, guides, technical documentation, and demo data; clean installation and use are reproducible.

**Phase 9 — Demonstration and handover**
- Prepare a fictional service-business scenario and rehearse a continuous 7–10 minute demonstration.
- Demonstrate customer/project setup, delivery tracking, submissions, approvals, costs, billing, payments, reporting, and role-based access.
- Present test evidence and known limitations honestly.
- **Outputs/check:** Working module, repository/README, guides, acceptance results, and repeatable demonstration; internship lead can follow the end-to-end workflow and receives the agreed deliverables.

## 4. Suggested Implementation Dependency Order

| Order | Area | Main focus |
|---|---|---|
| 1 | Customer and project foundation | Records, ownership, team, dates, budgets |
| 2 | Tasks, milestones, assignments | Delivery structure and progress |
| 3 | Worklogs and expenses | Hours and project expense submissions |
| 4 | Approval workflows/history | Review, approval/rejection, traceability |
| 5 | Recorded costs and budgets | Approved labour/expenses and utilization |
| 6 | Billing and payments | Billing, partial payments, outstanding balances |
| 7 | Dashboards and reports | Project/portfolio monitoring and printable reports |

Security, validation, and testing must be developed alongside features, not postponed. Independent work can proceed in parallel after shared models and interfaces are agreed.

## 5. Team Structure and Responsibilities

| Member | Primary role | Main responsibility |
|---|---|---|
| 1 | Product and Functional Lead | Requirements, workflows, Odoo setup, project/customer screens |
| 2 | Backend and Data Lead | Data models, constraints, approval transitions, calculations |
| 3 | UX, Views and Reporting Lead | Menus, views, dashboards, PDF project report |
| 4 | Security, QA and DevOps Lead | Access groups, record rules, test plan, deployment, documentation |

**Shared responsibilities:** Integration; peer review; decisions affecting multiple components; shared data contracts; end-to-end testing; demonstration preparation; and communication of blockers, dependencies, and changes.

### Team working agreements

- Use feature branches; do not push unfinished work directly to `main`.
- Use pull requests and peer review before merging.
- Agree on shared model/field names, relationships, and status values before dependent work begins.
- Integrate frequently; keep changes small enough to review and test.
- Track decisions, blockers, model changes, and integration issues in a shared record.
- Demonstrate integrated progress regularly and repeatedly test the complete workflow.
- Discuss scope changes with the team/supervisor before treating them as commitments.

## 6. Coordination and Integration

Before dependent work begins, affected members agree on model/field names, relationships, model/method ownership, status values/transitions, data needed by views/reports/calculations, dependencies, and integration expectations.

- Communicate shared-model/interface changes before merging.
- Integrate through reviewed pull requests and controlled merges.
- Resolve mismatches as they arise; verify connected functionality in the running application.
- Record integration defects, assign an owner, and update documentation when designs change.
- Maintain a shared decision record containing the decision, rationale, affected components, and people to inform.
- Raise blockers affecting shared models, security, integration, or scope promptly.

## 7. Project Deliverables

1. Working/deployable ProjectOps Odoo module implementing the agreed MVP.
2. GitHub repository and README.
3. User guide for main workflows.
4. Setup and installation documentation.
5. Acceptance test results covering workflows and role permissions.
6. Repeatable 7–10 minute demonstration using a fictional company scenario.

## 8. Success Criteria

| ID | Criterion | Evidence |
|---|---|---|
| SC-01 | Core workflow works from customer/project creation through approvals, cost recording, billing, and reporting. | End-to-end demo and acceptance tests |
| SC-02 | Dashboard figures match independent calculations. | Checks using known test data |
| SC-03 | No critical workflow or permission defect remains. | Final defect log and test results |
| SC-04 | A team member cannot access other members’ costs or project billing information. | Restricted-account permission tests |
| SC-05 | The system can be demonstrated repeatedly with a fictional company. | Rehearsed 7–10 minute demo |
| SC-06 | The project can be installed and understood from submitted documentation. | Setup verification and handover materials |

**Calculation example from the proposal**

| Item | Amount |
|---|---:|
| Approved labour | ETB 80,500 |
| Approved expenses | ETB 18,000 |
| **Recorded project cost** | **ETB 98,500** |
| Budget utilization | 32.83% |

Use this example to check dashboard figures against independent hand calculations.

## 9. Key Risks and Mitigation

| Risk | Potential impact | Mitigation |
|---|---|---|
| Scope creep | Extra features delay the core workflow. | Freeze must-have MVP scope; defer extras until core tests pass. |
| Odoo version/edition mismatch | Different behavior or unavailable apps. | Use Odoo 19 consistently and verify required apps in the agreed environment. |
| Weak access control | Users see information outside their responsibilities. | Implement role rules early and test with restricted accounts. |
| Late integration | Model, field, and dependency conflicts delay delivery. | Agree contracts early; merge small changes frequently with peer review. |

## 10. Shared Project Checkpoints

1. **Scope and environment confirmed:** Scope, Odoo 19, environment, and collaboration rules agreed.
2. **Requirements understood:** Roles, workflows, rules, and acceptance criteria documented.
3. **Architecture agreed:** Fit-gap, data model, security matrix, and interfaces reviewed.
4. **Module foundation works:** Module installs and upgrades reliably.
5. **Components demonstrated:** Each component meets its acceptance criteria.
6. **End-to-end integration works:** Main workflow runs across the application.
7. **Quality verified:** Acceptance, calculation, and permission tests pass.
8. **Handover ready:** Deployment, documentation, repository, and demonstration are ready.

## 11. Scope and Change Management

Keep the must-have MVP visible. For every proposed change:

1. Describe the requested change and its reason.
2. Assess effects on scope, dependencies, implementation, testing, and delivery.
3. Discuss it with affected team members.
4. Obtain team/supervisor agreement when it changes the agreed scope.
5. Record whether it is accepted or deferred and communicate the decision.
6. Update affected requirements, plans, and technical documents.

Quotation links, reminders, CSV exports, portals, and AI-assisted risk summaries are possible later enhancements, not MVP commitments unless the scope is formally revised.

## 12. Final Handover

Handover includes the working ProjectOps module, GitHub repository and README, user guide, setup documentation, acceptance test results, and repeatable fictional-company demonstration.

Present ProjectOps as one integrated solution: customer/project setup, delivery tracking, worklog and expense submissions, approvals, recorded costs, billing, payments, dashboards, reporting, and role-based access. Show testing evidence and explain known limitations honestly.

**Handover is complete when** the main workflow operates end to end, critical workflow and permission tests pass, all agreed deliverables are available, and the internship lead can follow the demonstration and documentation.
