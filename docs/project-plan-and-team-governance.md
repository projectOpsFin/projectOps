## Add-on structure of projectops

projectops folder will contain the ProjectOps-specific models, business logic, security configuration, views, menus, reporting and module resources.

The implementation should follow a modular internal structure so that backend logic, views, security and reports remain organized.

A suggested structure is:
```text
projectops_core/
│
├── __init__.py
├── __manifest__.py
│
├── models/
│   ├── __init__.py
│   ├── project_extension.py
│   ├── project_assignment.py
│   ├── project_milestone.py
│   ├── timesheet_extension.py
│   ├── expense_extension.py
│   ├── approval_log.py
│   └── financial_calculation.py
│
├── views/
│   ├── menus.xml
│   ├── project_views.xml
│   ├── task_views.xml
│   ├── milestone_views.xml
│   ├── assignment_views.xml
│   ├── worklog_views.xml
│   ├── expense_views.xml
│   ├── billing_views.xml
│   └── dashboard_views.xml
│
├── reports/
│   ├── project_report.xml
│   └── project_report_templates.xml
│
├── security/
│   ├── security_groups.xml
│   ├── ir.model.access.csv
│   └── record_rules.xml
│
├── data/
│
└── static/
```