# ProjectOps — Workflows and Business Rules

## 1. Purpose

This document defines the main business workflows, rules, validations, and important decisions governing ProjectOps. It describes expected business behavior rather than specific Odoo screens or Python implementation.

The workflows cover customer and project management, delivery tracking, worklog and expense approvals, billing, payments, and project monitoring.

## 2. System Actors

| Actor | Main responsibilities |
|---|---|
| Owner / Operations Manager | Monitors project performance, budgets, delays, reports, and outstanding balances. |
| Project Manager | Manages project delivery, tasks, milestones, progress, and reviews submissions where authorized. |
| Finance Officer | Manages project costs, billing records, and customer payments. |
| Team Member | Views assigned tasks, updates progress, and submits worklogs and expenses. |
| Customer | External party represented through customer records and billing; no customer login role is currently defined. |

Exact technical permissions and approval authority must follow the team's approved role-permission decisions.

## 3. Overall Business Workflow

The main ProjectOps lifecycle is:

**Customer → Project → Milestones and Tasks → Worklog and Expense Submission → Approval → Recorded Project Costs → Billing and Payments → Dashboards and Reports → Project Completion**

Each stage contributes information to the next. Only approved worklogs and expenses contribute to recorded project costs.

## 4. Customer and Project Workflow

1. An authorized user registers a customer.
2. A project is created and linked to that registered customer.
3. The project receives a unique project code, designated owner, assigned team, dates, contract value, and cost budget.
4. The project begins in Draft.
5. An authorized user activates the project.
6. Project activities are organized through milestones and tasks.

**Business rules**

- Every project must reference a registered customer.
- Every project must have a designated owner.
- A project may contain multiple assignments, milestones, tasks, worklogs, expenses, and invoices.
- Project records must retain their customer and ownership relationships.

## 5. Milestone and Task Workflow

1. A project is organized into milestones and tasks.
2. Tasks are assigned to team members.
3. Team members update task progress.
4. Managers monitor progress and identify overdue work.
5. Project progress is summarized for project monitoring.

**Business rules**

- Every milestone and task must belong to a valid project.
- A task may optionally belong to a milestone.
- Tasks support assignment, progress tracking, and overdue detection.
- The system provides a simple project progress measure.

The exact task and milestone statuses, progress formula, completion conditions, and reassignment behavior require team agreement.

## 6. Worklog Submission and Approval

1. A Team Member records time spent on project work.
2. The worklog is associated with the relevant project and, where applicable, task.
3. The Team Member submits the worklog.
4. An authorized approver reviews it.
5. The approver approves or rejects the submission.
6. An approved worklog contributes to recorded labour cost.

**Business rules**

- Submitted worklogs require an approval decision.
- Users cannot approve their own worklogs.
- Pending and rejected worklogs are excluded from recorded project cost.
- Approval history must identify the approver.
- The applicable hourly cost rate must be saved as a snapshot on each worklog so later rate changes do not alter historical costs.

The authorized approver, rejection-reason requirements, resubmission process, and correction of approved worklogs require team agreement.

## 7. Expense Submission and Approval

1. A Team Member records a project-related expense.
2. The expense is associated with the relevant project.
3. Supporting receipt information is attached.
4. The Team Member submits the expense.
5. An authorized approver reviews and approves or rejects it.
6. Approved expenses contribute to recorded project cost.

**Business rules**

- Expense submissions support receipt attachments.
- Users cannot approve their own expenses.
- Pending and rejected expenses are excluded from recorded project cost.
- Approval actions must be traceable to the person who made the decision.

The team must agree on mandatory receipt conditions, expense categories, rejection reasons, resubmission, and correction or reversal behavior.

## 8. Billing and Payment Workflow

1. A project-related billing record is created.
2. The Finance Officer manages invoice information.
3. Customer payments are recorded against the relevant invoice.
4. Full and partial payments are supported.
5. The system calculates the outstanding balance.
6. The system identifies overdue billing records.

**Business rules**

- An invoice may have multiple payment records.
- Outstanding balance = Invoice amount − Payments received.
- Overdue status is calculated using the agreed due-date rules.
- Payment tracking is separate from project delivery status.
- ProjectOps provides project-level billing visibility; it does not replace a full accounting system.

Invoice statuses, payment allocation, overpayments, refunds, reversals, and currency-rounding rules require team agreement.

## 9. Project Monitoring and Completion

Project and portfolio dashboards use project delivery and financial information.

The system supports monitoring of:

- Project progress and overdue work.
- Approved labour cost and approved expenses.
- Recorded project cost and budget utilization.
- Billing amounts and outstanding balances.
- Estimated project contribution.
- Project health indicators.

**Business rules**

- Project health uses transparent Red, Amber, Green, or Grey indicators.
- The exact rule or trigger must be displayed.
- Health indicators are warnings for management attention, not automated decisions.
- A health indicator must not automatically stop a project or change its budget.
- The financial measure is called **estimated project contribution**, not net profit.
- A project may be operationally completed while an invoice remains unpaid.

The team must agree on health thresholds, final project-completion conditions, and who can mark a project completed.

## 10. Core Business Rules

| ID | Business rule |
|---|---|
| BR-01 | Every project must belong to a registered customer. |
| BR-02 | Every project must have a designated owner. |
| BR-03 | Tasks and milestones must belong to a valid project. |
| BR-04 | Worklogs and expenses must be approved before contributing to recorded project cost. |
| BR-05 | Users cannot approve their own worklogs or expenses. |
| BR-06 | Approval actions must be attributable to a named approver. |
| BR-07 | Historical worklog costs use the hourly-rate snapshot recorded on the worklog. |
| BR-08 | Partial customer payments are supported. |
| BR-09 | Outstanding balance is calculated from invoice amounts and payments received. |
| BR-10 | Project completion is independent of invoice settlement. |
| BR-11 | Project health indicators must explain their triggering rules. |
| BR-12 | Team Members must not access restricted commercial data, including project billing information and other members' costs. |

## 11. Validation and Security Rules

- Validate that project-related records reference existing projects.
- Validate that worklog and expense approval actions are performed by authorized users.
- Reject attempts to approve one's own submissions.
- Exclude unapproved records from project-cost calculations.
- Enforce access restrictions on the server, not only by hiding menus or buttons.
- Record approval decisions and approver identity.
- Test permissions using separate accounts for all four internal roles.
- Reject direct requests that attempt to access restricted records or perform unauthorized actions.

## 12. Financial Calculations

| Metric | Calculation |
|---|---|
| Recorded labour cost | Approved hours × applicable hourly cost rate |
| Recorded project cost | Approved labour cost + approved expenses |
| Budget utilization | (Recorded project cost ÷ Project cost budget) × 100 |
| Outstanding billing balance | Invoice amount − Payments received |

**Reference example:** Approved labour of ETB 80,500 plus approved expenses of ETB 18,000 produces recorded project cost of ETB 98,500. For a project cost budget of ETB 300,000, budget utilization is 32.83%.

The team must agree on zero or missing budgets, rounding, currency precision, rate changes, adjusted transactions, and payment reversals before implementing the affected calculations.

## 13. Decisions Requiring Team Agreement

The source documents leave the following decisions unresolved:

| Area | Decision required |
|---|---|
| Customer and project access | Which roles may create and edit customers and projects? |
| Project lifecycle | Who activates projects? Can projects be cancelled, archived, or reopened? |
| Tasks and milestones | Which statuses and progress calculations will be used? |
| Worklog approvals | Which roles approve worklogs? How are rejection and resubmission handled? |
| Expense approvals | Who approves expenses? When are receipts mandatory? |
| Approved records | How are corrections, cancellations, and reversals handled? |
| Billing | Which invoice statuses and due-date rules apply? |
| Payments | How are overpayments, refunds, and payment reversals handled? |
| Project completion | Who confirms completion, and what conditions must be satisfied? |
| Project health | What exact conditions trigger Red, Amber, Green, or Grey? |
| Financial calculations | What currency, precision, rounding, and missing-budget rules apply? |

These decisions must be recorded and agreed before dependent implementation. Suggested workflow diagrams and proposed statuses must not be treated as approved specifications.

## 14. Document Maintenance

Update this document whenever the team approves a change to a workflow or business rule. Keep it consistent with the project requirements, system architecture, data model, technical contracts, and role-permission matrix.

**Document status:** Draft for team review.