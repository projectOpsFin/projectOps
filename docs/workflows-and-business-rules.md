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

**Current backend baseline rules (Step 2)**

- **Milestone statuses:** `planned` → `in_progress` → `completed` (or `cancelled`; `completed`/`cancelled` can be reopened to `planned`).
- **Task statuses:** `todo`, `in_progress`, `done`, `cancelled`.
- **Task completion behavior:** Marking a task `done` (`action_mark_done()` or writing `status='done'`) sets `state='1_done'` and `progress=100.0`. Setting `progress=100.0` manually does **not** auto-complete the task (so review/sign-off can still occur before marking `done`).
- **Project progress formula:** `Project Delivery Progress (%) = (Completed Tasks / Total Tasks) × 100` across active, non-cancelled tasks (`0.0` if no active non-cancelled tasks), rounded to 2 decimal places. This assumes equal weight per task.
- **Overdue detection:** A task is overdue when its `deadline` (or `date_deadline`) is strictly earlier than today (`< today`) and its status is neither `done` nor `cancelled` (and `not is_closed`). Tasks due today are not yet overdue.
- **Reassignment & assignment history:** `projectops.assignment` enforces `UNIQUE(project_id, user_id)` and uses `active` toggling for deactivation/reactivation, with `mail.thread` field tracking (`user_id`, `project_role`, `start_date`, `end_date`, `active`) providing an audit trail of changes.

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
| BR-13 | Completing a task (`done`) sets progress to 100%, while manually setting progress to 100% does not auto-complete the task. |
| BR-14 | A task is overdue only when its deadline is strictly earlier than today (`< today`) and it is not `done`, `cancelled`, or closed. |
| BR-15 | Each user may have at most one assignment record per project (`UNIQUE(project_id, user_id)`); reassignments toggle `active` and are audited via chatter tracking. |
| BR-16 | Project Managers can manage all projects, assignments, milestones, and tasks (without project unlink rights), while Operations Managers retain full portfolio and delete authority. |

## 11. Validation and Security Rules

- Validate that project-related records reference existing projects.
- Validate that worklog and expense approval actions are performed by authorized users.
- Reject attempts to approve one's own submissions.
- Exclude unapproved records from project-cost calculations.
- Enforce access restrictions on the server, not only by hiding menus or buttons.
- Record approval decisions and approver identity.
- Test permissions using separate accounts for all four internal roles.
- Reject direct requests that attempt to access restricted records or perform unauthorized actions.
- Restrict Team Members on `project.task` to updating only `progress`, `status`, `state`, and `description` on tasks assigned to them.
- Restrict Finance Officers to read-only access on projects, assignments, milestones, and tasks.

## 12. Project Calculation Formulas

| Metric | Formula |
|---|---|
| Recorded Labour Cost (RLC) | Approved Hours × Hourly Cost Rate Snapshot |
| Recorded Project Cost (RPC) | Recorded Labour Cost + Approved Project Expenses |
| Budget Utilization (%) | (RPC ÷ Project Cost Budget) × 100 |
| Outstanding Billing Balance | Billed Amount − Payments Received |
| Estimated Project Contribution | Contract Value − RPC |
| Project Delivery Progress (%) | (Completed Tasks ÷ Total Tasks) × 100 |

### 12.1 Recorded Labour Cost (RLC)

Recorded labour cost is the total cost of approved worklogs:

$$\text{RLC} = \sum_{i=1}^{n} (H_i \times R_i)$$

Where:
- $H_i$ = approved hours of worklog $i$
- $R_i$ = hourly cost rate snapshot of worklog $i$
- $n$ = number of approved worklogs

Only approved worklogs contribute to this calculation.

### 12.2 Recorded Project Cost (RPC)

Recorded project cost is the total approved labour cost plus approved project expenses:

$$\text{RPC} = \sum_{i=1}^{n} (H_i \times R_i) + \sum_{j=1}^{m} E_j$$

Where:
- $H_i$ = approved hours
- $R_i$ = hourly cost rate snapshot
- $E_j$ = amount of approved expense $j$
- $m$ = number of approved expenses

### 12.3 Budget Utilization (%)

Budget utilization shows how much of the project's cost budget has been used:

$$\text{Budget Utilization (\%)} = \frac{\text{RPC}}{\text{Project Cost Budget}} \times 100$$

**Example:** If recorded project cost is ETB 98,500 and cost budget is ETB 300,000, $\frac{98,500}{300,000} \times 100 = 32.83\%$. A utilization percentage greater than 100% means the recorded project cost has exceeded the budget.

### 12.4 Outstanding Billing Balance

This represents the amount the customer has not yet paid:

$$\text{Outstanding Billing Balance} = \text{Billed Amount} - \text{Payments Received}$$

**Example:** If the customer has been billed ETB 100,000 and has paid ETB 60,000, outstanding balance = $100,000 - 60,000 = \text{ETB } 40,000$.

### 12.5 Estimated Project Contribution

This represents the estimated contribution remaining after recorded project costs are deducted from the contract value:

$$\text{Estimated Project Contribution} = \text{Contract Value} - \text{RPC}$$

**Example:** If contract value is ETB 400,000 and recorded project cost is ETB 98,500, estimated project contribution = $400,000 - 98,500 = \text{ETB } 301,500$. This is an estimated project contribution, not net profit, because ProjectOps does not include all company accounting expenses.

### 12.6 Project Delivery Progress (%)

This measures the proportion of project tasks that have been completed:

$$\text{Project Delivery Progress (\%)} = \frac{\text{Completed Tasks}}{\text{Total Tasks}} \times 100$$

**Example:** If 8 out of 10 tasks are completed, $\frac{8}{10} \times 100 = 80\%$. This formula assumes that every task has equal weight (evaluated across active, non-cancelled tasks). If the team later agrees that tasks should have different weights, the formula would need to be revised.

The team must still agree on zero or missing budgets, rounding, currency precision, rate changes, adjusted transactions, and payment reversals before implementing the affected financial calculations.

## 13. Decisions Requiring Team Agreement

The source documents leave the following decisions unresolved:

| Area | Decision required |
|---|---|
| Customer and project access | Which roles may create and edit customers and projects? |
| Project lifecycle | Who activates projects? Can projects be cancelled, archived, or reopened? |
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