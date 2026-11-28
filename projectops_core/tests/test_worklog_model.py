# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestWorklogModel(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env['res.partner'].create({
            'name': 'Worklog Test Client',
            'is_projectops_customer': True,
        })
        cls.user_pm = cls.env['res.users'].create({
            'name': 'Worklog PM',
            'login': 'worklog_pm',
            'email': 'worklog_pm@example.com',
            'hourly_cost_rate': 120.0,
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_project_manager').id])],
        })
        cls.user_member = cls.env['res.users'].create({
            'name': 'Worklog Member',
            'login': 'worklog_member',
            'email': 'worklog_member@example.com',
            'hourly_cost_rate': 75.0,
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_team_member').id])],
        })
        cls.emp_member = cls.env['hr.employee'].create({
            'name': 'Worklog Member Emp',
            'user_id': cls.user_member.id,
            'hourly_cost': 75.0,
        })
        cls.user_unassigned = cls.env['res.users'].create({
            'name': 'Worklog Outsider',
            'login': 'worklog_outsider',
            'email': 'worklog_outsider@example.com',
            'hourly_cost_rate': 50.0,
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_team_member').id])],
        })

        cls.project = cls.env['project.project'].with_user(cls.user_pm).create({
            'project_code': 'PRJ-WL-01',
            'name': 'Worklog Project',
            'customer_id': cls.customer.id,
            'owner_user_id': cls.user_pm.id,
            'start_date': '2026-06-01',
            'contract_value': 100000.0,
            'cost_budget': 60000.0,
        })
        cls.other_project = cls.env['project.project'].with_user(cls.user_pm).create({
            'project_code': 'PRJ-WL-02',
            'name': 'Other Worklog Project',
            'customer_id': cls.customer.id,
            'owner_user_id': cls.user_pm.id,
            'start_date': '2026-06-01',
            'contract_value': 50000.0,
            'cost_budget': 30000.0,
        })
        cls.env['projectops.assignment'].with_user(cls.user_pm).create({
            'project_id': cls.project.id,
            'user_id': cls.user_member.id,
            'project_role': 'member',
        })
        cls.task = cls.env['project.task'].with_user(cls.user_pm).create({
            'project_id': cls.project.id,
            'title': 'Assigned Task',
            'assignee_user_id': cls.user_member.id,
        })
        cls.other_task = cls.env['project.task'].with_user(cls.user_pm).create({
            'project_id': cls.other_project.id,
            'title': 'Other Project Task',
            'assignee_user_id': cls.user_pm.id,
        })

    def test_create_worklog_and_project_task_links(self):
        """Timesheet worklog links to project and optional task and captures hourly_rate_snapshot."""
        worklog = self.env['account.analytic.line'].with_user(self.user_member).create({
            'project_id': self.project.id,
            'task_id': self.task.id,
            'date': '2026-06-10',
            'unit_amount': 4.5,
            'name': 'Implemented backend API',
        })
        self.assertEqual(worklog.status, 'draft')
        self.assertEqual(worklog.sudo().hourly_rate_snapshot, 75.0)
        self.assertIn(worklog, self.project.worklog_ids)
        self.assertEqual(self.project.worklog_count, 1)
        self.assertIn(worklog, self.task.worklog_ids)
        self.assertEqual(self.task.worklog_count, 1)

    def test_hourly_rate_snapshot_immutability(self):
        """Changing employee/user hourly rate after submission does not alter submitted snapshot."""
        worklog = self.env['account.analytic.line'].with_user(self.user_member).create({
            'project_id': self.project.id,
            'date': '2026-06-11',
            'unit_amount': 3.0,
            'name': 'Design review',
        })
        worklog.action_submit()
        self.assertEqual(worklog.status, 'submitted')
        self.assertEqual(worklog.sudo().hourly_rate_snapshot, 75.0)

        # Rate increases on hr.employee (and syncs to res.users) after submission
        self.emp_member.sudo().write({'hourly_cost': 110.0})
        self.assertEqual(self.user_member.sudo().hourly_cost_rate, 110.0)
        self.assertEqual(worklog.sudo().hourly_rate_snapshot, 75.0)

        # Manual override of snapshot is forbidden
        with self.assertRaises(UserError):
            worklog.sudo().write({'hourly_rate_snapshot': 999.0})

    def test_worklog_validation_constraints(self):
        """Validate positive hours, non-empty description, task-project match, and assignment."""
        with self.assertRaises(ValidationError):
            self.env['account.analytic.line'].with_user(self.user_member).create({
                'project_id': self.project.id,
                'unit_amount': 0.0,
                'name': 'Zero hours',
            })
        with self.assertRaises(ValidationError):
            self.env['account.analytic.line'].with_user(self.user_member).create({
                'project_id': self.project.id,
                'unit_amount': -2.0,
                'name': 'Negative hours',
            })
        with self.assertRaises(ValidationError):
            self.env['account.analytic.line'].with_user(self.user_member).create({
                'project_id': self.project.id,
                'unit_amount': 2.0,
                'name': '   ',
            })
        with self.assertRaises(ValidationError):
            self.env['account.analytic.line'].with_user(self.user_member).create({
                'project_id': self.project.id,
                'task_id': self.other_task.id,
                'unit_amount': 2.0,
                'name': 'Mismatched task',
            })
        with self.assertRaises(ValidationError):
            self.env['account.analytic.line'].sudo().create({
                'project_id': self.project.id,
                'user_id': self.user_unassigned.id,
                'unit_amount': 2.0,
                'name': 'Unassigned submitter',
            })
        with self.assertRaises(ValidationError):
            self.emp_member.sudo().write({'hourly_cost': -10.0})

    def test_worklog_lock_after_submission(self):
        """Submitted worklogs cannot be edited, deleted, or resubmitted."""
        worklog = self.env['account.analytic.line'].with_user(self.user_member).create({
            'project_id': self.project.id,
            'unit_amount': 5.0,
            'name': 'Initial draft',
        })
        worklog.action_submit()
        self.assertEqual(worklog.status, 'submitted')

        with self.assertRaises(UserError):
            worklog.sudo().write({'unit_amount': 8.0})
        with self.assertRaises(UserError):
            worklog.sudo().unlink()
        with self.assertRaises(UserError):
            worklog.action_submit()
        with self.assertRaises(UserError):
            worklog.sudo().write({'status': 'approved'})
