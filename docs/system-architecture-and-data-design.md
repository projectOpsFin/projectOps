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
│   │   ├── security.xml        # Security groups and rules
│   │   └── ir.model.access.csv # Model-level access rights
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
│   ├── 01-project-overview-and-requirements.md
│   ├── 02-system-architecture-and-data-design.md
│   ├── 03-workflows-and-business-rules.md
│   └── 04-project-plan-and-team-governance.md
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

| Business entity | Proposed Odoo model / starting point | Design note |
|---|---|---|
| Customer | `res.partner` or `projectops.customer` | Evaluate native Contacts before creating a separate model |
| Project | Native Project model or `projectops.project` | Confirm through fit-gap analysis |
| User | `res.users` | Reuse native Odoo users and security groups |
| Project Assignment | `projectops.assignment` | Proposed custom model |
| Milestone | Native Project functionality or `projectops.milestone` | Confirm whether extension or custom model is needed |
| Task | Native Project Task or `projectops.task` | Evaluate native task functionality |
| Worklog | Native Timesheets or `projectops.worklog` | Evaluate native timesheet functionality |
| Expense | Native Expenses or `projectops.expense` | Evaluate native expense functionality |
| Invoice | Native Accounting/Invoicing or `projectops.invoice` | Avoid duplicating accounting functionality |
| Payment | Native Accounting/Invoicing or `projectops.payment` | Confirm the required project-level payment tracking |
| Approval Log | `projectops.approval.log` | Proposed custom record of approval actions |

The team should not create duplicate customer, user, project, task or accounting models before completing the Odoo fit-gap review. The final module dependencies must also reflect the native Odoo features selected for use.

### 3.2 Key data relationships

- A customer can be associated with multiple projects; each project refers to its customer.
- A project has milestones, tasks and team assignments.
- An assignment links an Odoo user to a project and records the user's project role.
- Worklogs and expenses are submitted by users and linked to the relevant project; a worklog may also refer to a task.
- Invoice and payment records are associated with a project.
- Approval actions must be traceable through the approval history.

The final relationship definitions and field specifications must remain consistent with the approved ERD and shared technical contracts.

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

## 6. Technical Design Decisions to Confirm

The following items must be resolved and reflected in the ERD and technical contracts before dependent implementation is finalized:

1. Which native Odoo models and modules will be reused, extended or replaced by custom models.
2. Final model names, field names, data types, relationships and constraints.
3. Where user hourly cost rates are maintained and who may change them.
4. Exact workflow statuses, transitions, approval authority and rejection/resubmission rules.
5. Record-level access boundaries and visibility of financial and approval information.
6. Currency precision, cost calculations, payment adjustments and reversal handling.
7. Required module dependencies for the selected Odoo edition and environment.

Changes to shared models, fields, status values or method interfaces should be reviewed by affected team members and recorded in the shared technical contracts before implementation is changed.

## 7. Related Project Documents

- `01-project-overview-and-requirements.md` — project scope, actors and requirements.
- `03-workflows-and-business-rules.md` — business workflows, status transitions and calculations.
- `04-project-plan-and-team-governance.md` — implementation roadmap, responsibilities and team practices.

The architecture and data design should be kept consistent with the ProjectOps proposal, ERD, role-permission matrix, workflow diagrams and shared technical contracts. This document is a design baseline for review, not confirmation that all proposed technical decisions have been approved.
