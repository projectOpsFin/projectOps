# ProjectOps — System Architecture and Data Design

**Organization:** Keradion Technology  
**Project:** ProjectOps — Odoo-based Project Management and Business Operations Module  
**Document status:** Draft for team review  
**Version:** 0.1  
**Last updated:** 22 November 2026

## 1. Architecture Overview

ProjectOps will be developed as a custom Odoo add-on. Odoo provides the application framework, ORM, user and group management, views, messaging and reporting facilities. PostgreSQL is used as the database. ProjectOps-specific functionality will be implemented through the add-on and suitable native Odoo capabilities will be reused or extended after the fit-gap review.

The implementation must remain within the custom add-on; Odoo core files should not be modified.

```text
                         Users
        Owner / Operations Manager | Project Manager
          Finance Officer          | Team Member
                          |
                          v
                 Odoo Web Interface
                 Menus, Views, Reports
                          |
                          v
                  ProjectOps Add-on
                     projectops_core
                          |
             +------------+-------------+
             |            |             |
             v            v             v
        Business       Security      Reporting
        Models         and Rules     and QWeb
             |            |             |
             +------------+-------------+
                          |
                          v
                   Odoo ORM Layer
                          |
                          v
                     PostgreSQL
```

The diagram shows the logical application layers. The final division between native Odoo models and custom ProjectOps models depends on the fit-gap analysis and team agreement.

## 2. Repository and Module Structure

The repository contains the custom add-on and project documentation. The Odoo source/framework is maintained separately from this repository and is added to the local Odoo add-ons path during development.

```text
projectops/
│
├── projectops_core/
│   ├── __init__.py
│   ├── __manifest__.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── ...                 # Business models and model extensions
│   │
│   ├── security/
│   │   ├── projectops_security.xml # Security groups and rules
│   │   └── ir.model.access.csv     # Model-level access rights
│   │
│   ├── views/
│   │   ├── ...                 # Form, list, search views and menus
│   │
│   ├── data/
│   │   └── ...                 # Sequences and required initial data
│   │
│   ├── report/
│   │   ├── ...                 # QWeb report templates and actions
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   └── ...                 # Model, workflow and access tests
│   │
│   ├── wizard/                 # Only for required transient workflows
│   ├── controllers/            # Only if custom HTTP routes are required
│   ├── static/                 # Only if custom frontend assets are required
│   └── i18n/                   # Translation files, if required
│
├── docs/
│   ├── project-overview-and-requirements.md
│   ├── system-architecture-and-data-design.md
│   ├── workflows-and-business-rules.md
│   ├── project-plan-and-team-governance.md
│   └── implementation-status.md
│
├── README.md
└── .gitignore
```

The structure is the planned organization of the add-on. Optional directories should be added when their functionality is needed; they do not need to contain placeholder files at the start. Model files should be introduced after the related model and reuse decisions are agreed.

### Main module files

| File or directory | Responsibility |
|---|---|
| `__manifest__.py` | Module name, version, dependencies, and data files loaded by Odoo |
| `__init__.py` | Initializes the Python packages |
| `models/` | ProjectOps business models, fields, constraints, computed values and workflow methods |
| `security/` | Security groups, record rules and model access definitions |
| `views/` | Menus and Odoo user-interface views |
| `data/` | Sequences and other required initial records |
| `report/` | Printable project reports using QWeb |
| `tests/` | Automated tests for business logic, workflows and access restrictions |
| `wizard/` | Temporary models for guided multi-step operations, if needed |
| `controllers/` | Custom web routes or external endpoints, if required |
| `static/` | Custom frontend assets, if required |
| `i18n/` | Translation files, if required |

## 3. Data Model

The supplied ERD identifies the main business entities below. The technical contracts document proposes Odoo model names and field types as a starting point; these proposals are not final until reviewed and agreed by the team.

```text
Customer
   |
   | 1
   |----------------------< Project
                              |
                              | 1
             +----------------+----------------+
             |                |                |
             v                v                v
         Milestone          Task          Assignment >------ User
             |                |                |
             +----------------+                |
                              |                 |
                              v                 |
                           Worklog              |
                              |                 |
                              v                 |
                         Approval Log <---------+
                              ^
                              |
                           Expense

Project --------------------< Invoice
                                 |
                                 v
                              Payment
```

This is a high-level relationship view, not a replacement for the detailed ERD. Exact cardinalities, optional relationships and approval-log links must follow the agreed ERD and technical contracts.

### 3.1 Entity and Odoo model mapping

ProjectOps will be developed as a custom add-on that extends and integrates with Odoo 19. ProjectOps will use the Odoo framework, ORM, security mechanisms, views, reporting capabilities and existing business applications wherever appropriate.

#### 3.1.1 Reuse, extend and custom development

The team has approved three implementation approaches:

#### A. Reuse

Use existing Odoo models, applications and functionality without unnecessarily recreating them.

Examples:

- Reuse Odoo Contacts for customer records.
- Reuse Odoo users and security groups.
- Reuse native project, task, timesheet, expense and accounting functionality where suitable.

#### B. Extend

Inherit or configure existing Odoo functionality to support ProjectOps-specific requirements.

Examples:

- Add ProjectOps budget and financial fields to native project records.
- Add approval and historical cost information to native timesheet records.
- Connect project-related expenses to the appropriate project.
Extend native views to display ProjectOps information.

#### C. Custom development

Develop new models, workflows, calculations or interfaces when native Odoo functionality does not adequately satisfy the requirements.

Examples:

- ProjectOps approval history.
- Project-specific assignment information where native project membership is insufficient.
- project health indicators.
- Portfolio-level monitoring and reporting.

The guiding principle is:

Reuse existing Odoo capabilities first, extend them where ProjectOps requires additional functionality, and create custom components only for requirements that cannot be adequately supported by the existing platform.

The team should not create duplicate customer, user, project, task or accounting models before completing the Odoo fit-gap review. The final module dependencies must also reflect the native Odoo features selected for use.

| Functional Area | Odoo Starting Point | Approach | ProjectOps Responsibility |
|----------------|--------------------|----------|--------------------------|
| Customer management | `res.partner` | Reuse | Use native customer records. |
| User management | `res.users` | Reuse | Use native Odoo users and groups. |
| Employee information | `hr.employee` | Reuse + Extend | Maintain ProjectOps hourly cost information if approved by the team. |
| Project management | `project.project` | Reuse + Extend | Add ProjectOps-specific project and financial information. |
| Task management | `project.task` | Reuse + Configure + Extend | Use native tasks and add required ProjectOps relationships or fields. |
| Project assignments | Native project membership | Reuse + Custom | Use native membership where sufficient; add a custom assignment model if role and assignment-period requirements need it. |
| Milestones | Native project functionality, if available and sufficient | Reuse or Custom | Create a custom milestone model only if the selected Odoo environment does not adequately support the required workflow. |
| Worklogs / Timesheets | `account.analytic.line` | Reuse + Extend | Add ProjectOps approval and historical cost information. |
| Expenses | `hr.expense` | Reuse + Configure + Extend | Use native expense records and connect them to ProjectOps projects. |
| Approval history | No directly equivalent ProjectOps approval register | Custom | Maintain traceable worklog and expense approval decisions. |
| Recorded project cost | ProjectOps calculation logic | Custom | Calculate cost from approved worklogs and approved expenses. |
| Budget and financial indicators | `project.project` and ProjectOps calculations | Extend + Custom | Maintain project budgets and calculate utilization and contribution indicators. |
| Customer invoices | `account.move` | Reuse + Extend | Use native accounting invoices and connect them to projects where required. |
| Customer payments | `account.payment` and accounting reconciliation | Reuse | Use native payment and reconciliation information. |
| Individual project dashboard | Native project views | Reuse + Extend | Present ProjectOps project-level information. |
| Portfolio dashboard | ProjectOps dashboard functionality | Custom | Display portfolio-wide project and financial indicators. |
| Project health | ProjectOps calculation logic | Custom | Produce transparent rule-based health indicators. |
| Printable project report | Odoo QWeb reporting | Reuse + Custom | Develop a ProjectOps-specific project summary report. |
| Security | Odoo access groups and record rules | Reuse + Configure + Extend | Define ProjectOps-specific roles and record-level restrictions. |

### 3.2 Key data relationships

- A customer can be associated with multiple projects; each project refers to its customer.
- A project has milestones, tasks and team assignments.
- An assignment links an Odoo user to a project and records the user's project role.
- Worklogs and expenses are submitted by users and linked to the relevant project; a worklog may also refer to a task.
- Invoice and payment records are associated with a project.
- Approval actions must be traceable through the approval history.

The final relationship definitions and field specifications must remain consistent with the approved ERD and shared technical contracts.

### 3.3 Field definitions

The following tables translate the ERD into proposed Odoo fields. Names and types should be treated as the shared baseline unless the team agrees to a change.

The proposed field types translate the ERD attributes into Odoo ORM types; they are not field types explicitly specified in the ERD. The model names shown are the proposed ProjectOps names. Where the fit-gap review selects a native Odoo model (see section 3.1), the same field names and meanings apply as extensions of, or mappings to, that native model.

#### 3.3.1 Customer

**Model:** `res.partner` (Reuse + Extend)

| Field | Odoo field type | Required | Description |
|---|---|---|---|
| `name` | Char | Yes | Customer name |
| `email` | Char | No | Customer email |
| `phone` | Char | No | Customer phone |
| `billing_address` | Text | No | Customer billing address |
| `created_at` | Datetime | Automatic | Record creation timestamp |

#### 3.3.2 Project

**Model:** `project.project` (Reuse + Extend)

| Field | Odoo field type | Required | Description |
|---|---|---|---|
| `project_code` | Char | Yes | Unique project code |
| `customer_id` | Many2one | Yes | Related customer |
| `owner_user_id` | Many2one | Yes | Project owner; relates to `res.users` |
| `name` | Char | Yes | Project name |
| `start_date` | Date | Yes | Project start date |
| `end_date` | Date | No | Planned project end date |
| `contract_value` | Monetary | Yes | Agreed contract value |
| `cost_budget` | Monetary | Yes | Project cost budget |
| `currency_id` | Many2one | Yes | Currency reference |
| `state` | Selection | Yes | Project lifecycle status |

Constraints:
- `project_code` must be unique.
- `end_date` must not be earlier than `start_date`.
- Contract value and cost budget must follow the agreed non-negative validation rules.

#### 3.3.3 User & Employee Hourly Rate

**Native models:** `res.users` & `hr.employee` (`hr_hourly_cost`) — Reuse + Extend

| Field | Model | Odoo field type | Description |
|---|---|---|---|
| `name` | `res.users` | Native Char | User name |
| `login` / `email` | `res.users` | Native fields | User login and contact information |
| `hourly_cost` | `hr.employee` | Native Monetary (`hr_hourly_cost`) | Employee's applicable hourly cost rate |
| `hourly_cost_rate` | `res.users` | Monetary (ProjectOps) | User's hourly cost rate, bidirectionally synced with `hr.employee.hourly_cost` |
| `active` | `res.users` | Native Boolean | Whether the user is active |

The ERD shows a role/security group attribute. In Odoo, role permissions are assigned through security groups rather than a text role field. Hourly cost rates are maintained by Operations Managers, Project Managers, and Finance Officers, and are hidden from Team Members (`BR-12`). Worklogs capture the applicable rate as an immutable historical snapshot (`hourly_rate_snapshot`).

#### 3.3.4 Project Assignment

**Proposed model:** `projectops.assignment`

| Field | Odoo field type | Required | Description |
|---|---|---|---|
| `project_id` | Many2one | Yes | Related project |
| `user_id` | Many2one | Yes | Assigned Odoo user |
| `project_role` | Selection | Yes | User's responsibility in this project |
| `start_date` | Date | No | Assignment start |
| `end_date` | Date | No | Assignment end |
| `active` | Boolean | Yes | Whether assignment is active |

Constraint: A user should not have duplicate assignment records for the same project. The ERD specifies a unique combination of project and user.

#### 3.3.5 Milestone

**Proposed model:** `projectops.milestone`

| Field | Odoo field type | Required | Description |
|---|---|---|---|
| `project_id` | Many2one | Yes | Related project |
| `title` | Char | Yes | Milestone title |
| `description` | Text | No | Milestone details |
| `due_date` | Date | No | Target completion date |
| `status` | Selection | Yes | Milestone status |
| `sequence` | Integer | Yes | Display order |

#### 3.3.6 Task

**Model:** `project.task` (Reuse + Extend)

| Field | Odoo field type | Required | Description |
|---|---|---|---|
| `project_id` | Many2one | Yes | Related project |
| `projectops_milestone_id` | Many2one | No | Related `projectops.milestone` (named `projectops_milestone_id` to avoid conflicting with native `project.task.milestone_id` which targets `project.milestone`) |
| `assignee_user_id` | Many2one | Yes | Assigned user (synced with native `user_ids`) |
| `title` | Char | Yes | Task title (synced with native `name`) |
| `description` | Html | No | Task details (native `project.task.description`) |
| `deadline` | Date | No | Task deadline (synced with native `date_deadline`) |
| `status` | Selection | Yes | Task status (`todo`, `in_progress`, `done`, `cancelled`; synced with native `state`) |
| `progress` | Float | Yes | Task progress percentage (`0`–`100`) |

Validation: Progress must remain between 0 and 100. Calling `action_mark_done()` (or setting `status` to `done`) automatically sets `progress` to `100.0`.

#### 3.3.7 Worklog

**Model:** `account.analytic.line` (`hr_timesheet` — Reuse + Extend)

| Field | Odoo field type | Required | Description |
|---|---|---|---|
| `project_id` | Many2one | Yes | Related `project.project` (native `hr_timesheet`) |
| `task_id` | Many2one | No | Related `project.task` within the same project (native `hr_timesheet`) |
| `user_id` | Many2one | Yes | Submitting `res.users` (native `analytic`) |
| `employee_id` | Many2one | Yes | Related `hr.employee`, auto-resolved/created for the user if needed (native `hr_timesheet`) |
| `date` | Date | Yes | Date the work was performed (native `analytic`) |
| `unit_amount` | Float | Yes | Number of hours worked; must be strictly positive (native `analytic`) |
| `name` | Char | Yes | Work performed description; cannot be empty (native `analytic`) |
| `currency_id` | Many2one | Yes | Currency reference (native `analytic`) |
| `hourly_rate_snapshot` | Monetary | Yes | Immutable historical hourly cost rate captured at creation/submission (restricted to PM/Finance/Ops Manager) |
| `status` | Selection | Yes | Submission status (`draft`, `submitted`, `approved`, `rejected`) |

`project.project` and `project.task` expose `worklog_ids` (`One2many('account.analytic.line', ...)`) and `worklog_count`. A later change to `hr.employee.hourly_cost` or `res.users.hourly_cost_rate` does not alter `hourly_rate_snapshot` on existing worklogs.

#### 3.3.8 Expense

**Model:** `hr.expense` (`hr_expense` — Reuse + Extend)

| Field | Odoo field type | Required | Description |
|---|---|---|---|
| `project_id` | Many2one | Yes | Related `project.project` |
| `employee_id` | Many2one | Yes | Related `hr.employee`, auto-resolved/created for the submitter if needed (native `hr_expense`) |
| `submitter_user_id` | Many2one | Yes | Submitting `res.users`, synced with `employee_id.user_id` |
| `date` | Date | Yes | Expense date (native `hr_expense`) |
| `category` | Selection | Yes | Standardized ProjectOps category (`travel`, `accommodation`, `meals`, `software`, `hardware`, `materials`, `other`) |
| `total_amount` / `total_amount_currency` | Monetary | Yes | Expense amount; must be strictly positive (native `hr_expense`) |
| `currency_id` | Many2one | Yes | Currency reference (native `hr_expense`) |
| `name` | Char | Yes | Expense description/summary; cannot be empty (native `hr_expense`) |
| `description` | Text | No | Additional internal notes (native `hr_expense`) |
| `receipt_file` / `receipt_filename` | Binary / Char | Conditional | Optional direct receipt upload alongside native `attachment_ids` / `message_main_attachment_id`; at least one receipt attachment is required on `action_submit()` |
| `status` | Selection | Yes | ProjectOps submission status (`draft`, `submitted`, `approved`, `rejected`), synced with `hr.expense.approval_state` |

`project.project` exposes `expense_ids` (`One2many('hr.expense', 'project_id')`) and `expense_count`.

#### 3.3.9 Invoice

**Proposed model:** `projectops.invoice`

| Field | Odoo field type | Required | Description |
|---|---|---|---|
| `project_id` | Many2one | Yes | Related project |
| `invoice_number` | Char | Yes | Unique invoice reference |
| `amount` | Monetary | Yes | Invoice amount |
| `currency_id` | Many2one | Yes | Currency reference |
| `issue_date` | Date | Yes | Issue date |
| `due_date` | Date | Yes | Payment due date |
| `status` | Selection | Yes | Invoice lifecycle status |

The invoice model is intended for the ProjectOps billing register unless the fit-gap review selects native Odoo invoicing.

#### 3.3.10 Payment

**Proposed model:** `projectops.payment`

| Field | Odoo field type | Required | Description |
|---|---|---|---|
| `invoice_id` | Many2one | Yes | Related invoice |
| `amount` | Monetary | Yes | Payment amount |
| `currency_id` | Many2one | Yes | Currency reference |
| `payment_date` | Date | Yes | Payment date |
| `payment_reference` | Char | No | Payment reference |

The proposal requires support for full and partial payments. Reversal and adjustment behavior must be agreed with Activity 5 before implementation.

#### 3.3.11 Approval Log

**Proposed model:** `projectops.approval.log`

| Field | Odoo field type | Required | Description |
|---|---|---|---|
| `approver_user_id` | Many2one | Yes | User making the decision |
| `worklog_id` | Many2one | Conditional | Related worklog |
| `expense_id` | Many2one | Conditional | Related expense |
| `decision` | Selection | Yes | Approval decision |
| `decided_at` | Datetime | Yes | Decision timestamp |
| `comment` | Text | No | Approval or rejection comment |

Constraint: Each approval log entry must refer to exactly one worklog or one expense, not both.

Approval records must preserve the identity of the approver and the decision made.

### 3.4 Model relationships

The following relationships are based on the supplied ERD.

| Parent model | Related model | Relationship | Odoo field on child |
|---|---|---|---|
| Customer | Project | One-to-many | `customer_id` |
| User | Project | One-to-many | `owner_user_id` |
| Project | Project Assignment | One-to-many | `project_id` |
| User | Project Assignment | One-to-many | `user_id` |
| Project | Milestone | One-to-many | `project_id` |
| Project | Task | One-to-many | `project_id` |
| Milestone | Task | One-to-many | `milestone_id` |
| User | Task | One-to-many | `assignee_user_id` |
| Project | Worklog | One-to-many | `project_id` |
| Task | Worklog | One-to-many | `task_id` |
| User | Worklog | One-to-many | `submitted_by_user_id` |
| Project | Expense | One-to-many | `project_id` |
| User | Expense | One-to-many | `submitter_user_id` |
| Project | Invoice | One-to-many | `project_id` |
| Invoice | Payment | One-to-many | `invoice_id` |
| User | Approval Log | One-to-many | `approver_user_id` |
| Worklog | Approval Log | One-to-many | `worklog_id` |
| Expense | Approval Log | One-to-many | `expense_id` |

#### Relationship rules

1. Every project must belong to one customer.
2. Every project must have one designated owner.
3. A project may have multiple assignments, milestones, tasks, worklogs, expenses and invoices.
4. A task may optionally belong to a milestone.
5. A worklog may optionally reference a task.
6. An invoice may have multiple payment records.
7. Approval history must identify the user who made each decision.
8. Project assignments must prevent duplicate assignments for the same project and user (`UNIQUE(project_id, user_id)`).

## 4. Data Integrity and Business Constraints

The following requirements affect the data model and must be enforced in server-side model logic and, where appropriate, database constraints:

- Project codes must be unique.
- A project's end date must not be earlier than its start date.
- Project contract value and cost budget must follow the agreed non-negative validation rules.
- A user should not have duplicate assignments to the same project.
- Task progress must remain between 0 and 100.
- A worklog must retain the hourly cost rate applicable when it was recorded. Later changes to a user's rate must not change historical worklog cost.
- Only approved worklogs and approved expenses contribute to recorded project cost.
- A user must not approve their own worklog or expense.
- Approval actions must record the responsible approver and action history.
- Each approval log entry must refer to exactly one worklog or one expense, not both.
- Invoice numbers must be unique.
- Monetary calculations must use the project's agreed currency and precision rules.

Specific status values, transition rules, rejection/resubmission behavior, rounding rules and correction procedures remain subject to team agreement where they are not yet defined in the source documents.

## 5. Security Architecture

Access control will use Odoo security groups, model access rights and record rules. Sensitive operations, including approval and financial calculations, must also be checked on the server side. Hiding a menu or button is not sufficient protection.

The four internal roles are:

- **Owner / Operations Manager** — portfolio oversight and management-level project and financial visibility.
- **Project Manager** — project delivery, milestones, tasks and review of submitted work, subject to agreed approval authority.
- **Finance Officer** — billing records, payment tracking and relevant financial information.
- **Team Member** — assigned work, task updates and submission of worklogs and expenses; no access to commercial data.

The role-permission matrix is a draft. Permissions marked TBD must be agreed before they are implemented; TBD must not be treated as unrestricted access. The exact approval authority, record scope and visibility of approval history remain team decisions. Customer is currently treated as an external party represented by a customer record; customer login access is not defined in the project scope.

## 6. Shared Interfaces and Methods

The following method names are proposed contracts for communication between components. The team should use consistent names and behavior.

| Model | Method | Expected behavior |
|---|---|---|
| Worklog | `action_submit()` | Validate and submit a worklog |
| Worklog | `action_approve()` | Approve an eligible submitted worklog |
| Worklog | `action_reject()` | Reject a submitted worklog |
| Expense | `action_submit()` | Validate and submit an expense |
| Expense | `action_approve()` | Approve an eligible submitted expense |
| Expense | `action_reject()` | Reject a submitted expense |
| Task | `action_mark_done()` | Mark a task as completed after validation |
| Project | `action_activate()` | Activate an eligible project |
| Project | `action_complete()` | Complete a project according to agreed completion rules |
| Invoice | `action_register_payment()` | Register a payment against an invoice |

### 6.1 Interface expectations

**Worklog and expense components**
- Create records using the agreed field names.
- Submit records through the agreed submission methods.
- Expose the agreed status and approval information.

**Approval component**
- Read submitted records.
- Apply authorization and no-self-approval checks.
- Record the approver, decision, timestamp and comment.
- Update the submission status.

**Calculation component**
- Read approved worklogs and expenses only when calculating recorded project cost.
- Use the agreed hourly rate snapshot.
- Follow the calculation rules agreed in Activity 5.

**Dashboard and reporting component**
- Read the agreed project, task, cost, billing and payment fields.
- Use the agreed calculation methods or computed fields rather than implementing separate conflicting formulas.

Method names for calculation fields and methods must be finalized with the Activity 5 owner.

## 7. Technical Design Decisions to Confirm

The following items must be resolved and reflected in the ERD and technical contracts before dependent implementation is finalized:

1. Which native Odoo models and modules will be reused, extended or replaced by custom models.
2. Final model names, field names, data types, relationships and constraints.
3. Where user hourly cost rates are maintained and who may change them.
4. Exact workflow statuses, transitions, approval authority and rejection/resubmission rules.
5. Record-level access boundaries and visibility of financial and approval information.
6. Currency precision, cost calculations, payment adjustments and reversal handling.
7. Required module dependencies for the selected Odoo edition and environment.
8. Approval method names and authorization behavior.
9. Calculation method names and computed-field dependencies.
10. Which fields and relationships are needed by screens and reports.
11. Project assignment and ownership rules used by record rules.

Changes to shared models, fields, status values or method interfaces should be reviewed by affected team members and recorded in the shared technical contracts before implementation is changed.

## 8. Related Project Documents

- `project-overview-and-requirements.md` — project scope, actors and requirements.
- `workflows-and-business-rules.md` — business workflows, status transitions and calculations.
- `project-plan-and-team-governance.md` — implementation roadmap, responsibilities and team practices.
- `implementation-status.md` — current repository implementation baseline and test coverage.

The architecture and data design should be kept consistent with the ProjectOps proposal, ERD, role-permission matrix, workflow diagrams and shared technical contracts. This document is a design baseline for review, not confirmation that all proposed technical decisions have been approved.
