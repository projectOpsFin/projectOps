# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestProgressAndOverdue(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env['res.partner'].create({
            'name': 'Monitoring Test Client',
            'is_projectops_customer': True,
        })
        cls.pm = cls.env['res.users'].create({
            'name': 'Monitoring PM',
            'login': 'monitoring_pm_test',
            'email': 'monitoring_pm@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_project_manager').id])],
        })
        cls.project = cls.env['project.project'].create({
            'project_code': 'PRJ-MON-01',
            'name': 'Monitoring Project',
            'customer_id': cls.customer.id,
            'owner_user_id': cls.pm.id,
            'start_date': '2026-01-01',
            'contract_value': 100000.0,
            'cost_budget': 50000.0,
        })

    def test_project_progress_calculation(self):
        """Test that project progress follows (Completed Tasks / Total Tasks) * 100 for non-cancelled tasks."""
        self.assertEqual(self.project.progress, 0.0)

        t1 = self.env['project.task'].with_user(self.pm).create({
            'project_id': self.project.id,
            'title': 'Task 1',
            'assignee_user_id': self.pm.id,
            'progress': 50.0,
        })
        t2 = self.env['project.task'].with_user(self.pm).create({
            'project_id': self.project.id,
            'title': 'Task 2',
            'assignee_user_id': self.pm.id,
            'progress': 100.0,
            'status': 'done',
        })
        t3 = self.env['project.task'].with_user(self.pm).create({
            'project_id': self.project.id,
            'title': 'Cancelled Task',
            'assignee_user_id': self.pm.id,
            'progress': 0.0,
            'status': 'cancelled',
        })

        # 1 completed (t2) out of 2 active non-cancelled tasks (t1, t2) = 50.0%; t3 is cancelled and excluded
        self.assertEqual(self.project.progress, 50.0)

        t1.action_mark_done()
        self.assertEqual(self.project.progress, 100.0)
        self.assertEqual(t3.status, 'cancelled')

    def test_overdue_detection_and_search(self):
        """Test overdue detection based on deadline and completion/cancellation status."""
        today = fields.Date.context_today(self.project)
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        overdue_task = self.env['project.task'].with_user(self.pm).create({
            'project_id': self.project.id,
            'title': 'Late Open Task',
            'assignee_user_id': self.pm.id,
            'deadline': yesterday,
            'status': 'in_progress',
        })
        done_past_task = self.env['project.task'].with_user(self.pm).create({
            'project_id': self.project.id,
            'title': 'Completed Past Task',
            'assignee_user_id': self.pm.id,
            'deadline': yesterday,
            'status': 'done',
        })
        cancelled_past_task = self.env['project.task'].with_user(self.pm).create({
            'project_id': self.project.id,
            'title': 'Cancelled Past Task',
            'assignee_user_id': self.pm.id,
            'deadline': yesterday,
            'status': 'cancelled',
        })
        future_task = self.env['project.task'].with_user(self.pm).create({
            'project_id': self.project.id,
            'title': 'Future Task',
            'assignee_user_id': self.pm.id,
            'deadline': tomorrow,
            'status': 'todo',
        })

        self.assertTrue(overdue_task.is_overdue)
        self.assertFalse(done_past_task.is_overdue)
        self.assertFalse(cancelled_past_task.is_overdue)
        self.assertFalse(future_task.is_overdue)

        self.assertEqual(self.project.overdue_task_count, 1)
        self.assertTrue(self.project.has_overdue_tasks)

        found_overdue = self.env['project.task'].search([
            ('project_id', '=', self.project.id),
            ('is_overdue', '=', True),
        ])
        self.assertEqual(found_overdue, overdue_task)

        # Marking overdue task done removes it from overdue count
        overdue_task.action_mark_done()
        self.assertFalse(overdue_task.is_overdue)
        self.assertEqual(self.project.overdue_task_count, 0)
        self.assertFalse(self.project.has_overdue_tasks)
