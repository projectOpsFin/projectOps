# ProjectOps --- Project Overview and Requirements

## 1. Project Overview

### 1.1 Project Background

Keradion Technology's project operations involve connected information
about customers, projects, delivery activities, team contributions,
project costs, and billing. When these details are managed across
separate spreadsheets, conversations, notes, or standalone tools, it can
be difficult to maintain a consistent view of project progress, budget
utilization, recorded costs, and outstanding customer payments.

ProjectOps is an Odoo-based project management and business operations
system intended to bring these areas together in one traceable
application. Its initial use is internal: the system is being developed
for Keradion Technology to manage its own projects and related
operations. Its requirements and role structure should nevertheless
remain reusable for other small and medium-sized service businesses in
the future.

### 1.2 Project Purpose

The purpose of ProjectOps is to connect project delivery information
with project-level financial visibility. It is intended to give
management a consolidated view of project progress and relevant
financial information, while enabling team members to manage assigned
work and submit time and expenses through an approval process.

ProjectOps is a focused operational system. It is not intended to
replace a full accounting, payroll, human resources, procurement, or
inventory system.

### 1.3 Project Aim

To develop a focused project management and business operations system
that provides Keradion Technology with a consolidated view of project
progress and project-level financial information, while retaining a
structure that can be reused by other service businesses.

## 2. Project Objectives

ProjectOps aims to:

1.  Maintain customer records and a structured project register
    containing project ownership, assigned team, dates, contract value,
    and cost budget.
2.  Organize project delivery through milestones, tasks, assignments,
    progress tracking, and overdue detection.
3.  Record working hours and project-related expenses through submission
    and approval capabilities.
4.  Track project billing records, partial payments, outstanding
    balances, and overdue billing status.
5.  Provide project-level and portfolio-level dashboards using
    documented calculation rules.
6.  Protect information through role-appropriate access and maintain
    traceability of approval actions.
7.  Provide printable project summaries, user documentation, and
    acceptance tests for the main system capabilities.

## 3. Target Users and Roles

### 3.1 Intended Users

The initial users of ProjectOps are Keradion Technology staff involved
in project oversight, project delivery, finance, and assigned project
work. The role structure and requirements are designed to remain
applicable to other small and medium-sized service businesses if the
system is reused in the future.

### 3.2 System Roles

| Role | Primary responsibilities |
|---|---|
| **Owner / Operations Manager** | Oversees business operations and project performance; monitors portfolio-level progress, project budgets, delays, unpaid balances, and project reports. |
| **Project Manager** | Manages project delivery; organizes tasks and milestones, monitors progress, and reviews submitted worklogs and expenses where authorized. |
| **Finance Officer** | Manages project-related financial records, including billing and payment tracking; records full or partial customer payments and monitors outstanding balances. |
| **Team Member** | Performs assigned project work, views assigned tasks, updates task progress, and submits worklogs and project-related expenses for review. |

A customer is represented in ProjectOps through customer records and
related billing information. The current project scope does not define a
customer-facing login role.

## 4. Project Scope

### 4.1 In Scope --- Minimum Viable Product

The ProjectOps MVP includes the following capabilities:

-   **Customer and project register:** Maintain customer records and
    projects, including a unique project code, owner, assigned team,
    dates, contract value, and cost budget.
-   **Tasks and milestones:** Define project milestones and tasks,
    assign team members, track progress, and identify overdue work.
-   **Worklogs and expenses:** Allow team members to submit working
    hours and project-related expenses, including supporting receipt
    attachments.
-   **Review and approval:** Support the review, approval, and rejection
    of submitted worklogs and expenses, with prevention of
    self-approval.
-   **Project cost tracking:** Record project costs using approved work
    hours and approved expenses.
-   **Billing and payments:** Maintain project-related billing records,
    record partial payments, calculate remaining balances, and identify
    overdue billing.
-   **Dashboards and metrics:** Present project-level and
    portfolio-level information, including recorded project cost, budget
    utilization, estimated project contribution, and outstanding
    billing.
-   **Project health indicators:** Display transparent Red, Amber,
    Green, or Grey indicators with the rule or trigger shown. These
    indicators provide early warnings for management attention.
-   **Security and auditability:** Enforce role-appropriate access on
    the server and maintain traceability of approval actions.
-   **Project reporting:** Provide a printable project summary report.
-   **Project handover materials:** Include fictional demonstration
    data, application setup and user documentation, and acceptance tests
    covering the main workflow and role permissions.

### 4.2 Out of Scope for the MVP

The following capabilities are outside the MVP scope:

-   Full accounting and tax-compliance functionality.
-   Payroll and human resources management.
-   Procurement and inventory management.
-   Payment gateway integration.
-   A separate React or mobile front end.
-   AI functionality that approves submissions or makes operational
    decisions.

Potential later enhancements such as quotation links, reminders, CSV
exports, portals, and AI-assisted risk summaries are not part of the MVP
unless the project scope is formally revised.

## 5. Functional Requirements

The following functional requirements describe the capabilities the MVP
must provide.

| ID | Requirement | Description |
|---|---|---|
| **FR-01** | Customer management | The system must allow authorized users to register and manage customer records. |
| **FR-02** | Project management | The system must allow authorized users to create and manage projects linked to registered customers. |
| **FR-03** | Task and milestone management | The system must support defining project tasks and milestones and tracking their progress. |
| **FR-04** | Worklog submission | Team Members must be able to submit worklogs for work performed on projects. |
| **FR-05** | Worklog approval | Authorized users must be able to review and approve or reject submitted worklogs. |
| **FR-06** | Expense submission | Team Members must be able to submit project-related expenses. |
| **FR-07** | Expense approval | Authorized users must be able to review and approve or reject submitted expenses. |
| **FR-08** | Project cost tracking | The system must record project costs based on approved worklogs and approved expenses. |
| **FR-09** | Billing management | The system must support project-related billing and invoice records. |
| **FR-10** | Payment tracking | The system must allow Finance Officers to record full and partial customer payments against invoices. |
| **FR-11** | Project monitoring | The system must display project delivery and financial metrics. |
| **FR-12** | Project health indicators | The system must use transparent, rule-based indicators to flag potentially at-risk projects for management attention. |
| **FR-13** | Reporting | The system must support dashboards and printable project reports. |
| **FR-14** | Access and audit support | The system must support role-appropriate access and traceability of relevant actions. |

## 6. Non-Functional Requirements

The following non-functional requirements describe the expected quality
and operational characteristics of ProjectOps.

| ID | Requirement | Description |
|---|---|---|
| **NFR-01** | Security | Users must only access information and perform actions they are authorized to access or perform. |
| **NFR-02** | Reliability | Project and financial calculations must be consistent and dependable. |
| **NFR-03** | Usability | Users should be able to understand relevant project information, assigned tasks, and record statuses without unnecessary difficulty. |
| **NFR-04** | Maintainability | The custom ProjectOps functionality should be organized so that it can be maintained and extended without modifying Odoo core code. |
| **NFR-05** | Performance | Dashboards and ordinary system operations should respond within an acceptable time. |

## 7. Project Boundaries

ProjectOps focuses on project delivery management and project-level
financial visibility. It provides operational billing and payment
tracking, but it is not a complete accounting solution. Its project
health indicators are intended to inform management by displaying
transparent warnings; they do not make operational decisions
automatically.

The MVP is intended to deliver a complete, secure, documented, and
tested core workflow rather than a full ERP suite.
