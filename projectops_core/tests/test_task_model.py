# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestTaskModel(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env['res.partner'].create({
            'name': 'Task Test Client',
            'is_projectops_customer': True,
        })
        cls.pm = cls.env['res.users'].create({
            'name': 'Task PM',
            'login': 'task_pm_test',
            'email': 'task_pm@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_project_manager').id])],
        })
        cls.member = cls.env['res.users'].create({
            'name': 'Task Member',
            'login': 'task_member_test',
            'email': 'task_member@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_team_member').id])],
        })
        cls.project_a = cls.env['project.project'].create({
            'project_code': 'PRJ-TASK-A',
            'name': 'Project Alpha',
            'customer_id': cls.customer.id,
            'owner_user_id': cls.pm.id,
            'start_date': '2026-04-01',
            'contract_value': 100000.0,
            'cost_budget': 50000.0,
        })
        cls.project_b = cls.env['project.project'].create({
            'project_code': 'PRJ-TASK-B',
            'name': 'Project Beta',
            'customer_id': cls.customer.id,
            'owner_user_id': cls.pm.id,
            'start_date': '2026-04-01',
            'contract_value': 100000.0,
            'cost_budget': 50000.0,
        })
        cls.milestone_a = cls.env['projectops.milestone'].create({
            'project_id': cls.project_a.id,
            'title': 'Alpha Milestone 1',
        })
        cls.milestone_b = cls.env['projectops.milestone'].create({
            'project_id': cls.project_b.id,
            'title': 'Beta Milestone 1',
        })

    def test_task_requires_valid_project(self):
        """Test that creating a task without a project is rejected."""
        with self.assertRaises(ValidationError):
            self.env['project.task'].with_user(self.pm).create({
                'title': 'Orphan Task',
                'assignee_user_id': self.member.id,
            })

    def test_task_requires_assignee(self):
        """Test that creating a task without an assignee is rejected per architecture docs."""
        with self.assertRaises(ValidationError):
            self.env['project.task'].with_user(self.pm).create({
                'project_id': self.project_a.id,
                'title': 'Unassigned Task',
            })

    def test_task_with_optional_milestone(self):
        """Test creating tasks with and without a milestone in the same project."""
        task_no_ms = self.env['project.task'].with_user(self.pm).create({
            'project_id': self.project_a.id,
            'title': 'Task Without Milestone',
            'assignee_user_id': self.member.id,
            'deadline': '2026-07-01',
        })
        self.assertFalse(task_no_ms.projectops_milestone_id)
        self.assertEqual(task_no_ms.name, 'Task Without Milestone')
        self.assertEqual(task_no_ms.assignee_user_id, self.member)
        self.assertIn(self.member, task_no_ms.user_ids)

        task_with_ms = self.env['project.task'].with_user(self.pm).create({
            'project_id': self.project_a.id,
            'projectops_milestone_id': self.milestone_a.id,
            'title': 'Task With Milestone',
            'assignee_user_id': self.member.id,
        })
        self.assertEqual(task_with_ms.projectops_milestone_id, self.milestone_a)
        self.assertIn(task_with_ms, self.milestone_a.task_ids)

    def test_task_cannot_reference_other_project_milestone(self):
        """Test that a task cannot reference a milestone from another project."""
        with self.assertRaises(ValidationError):
            self.env['project.task'].with_user(self.pm).create({
                'project_id': self.project_a.id,
                'projectops_milestone_id': self.milestone_b.id,
                'title': 'Cross-Project Milestone Task',
                'assignee_user_id': self.member.id,
            })

    def test_task_progress_bounds(self):
        """Test that task progress must stay between 0 and 100."""
        task = self.env['project.task'].with_user(self.pm).create({
            'project_id': self.project_a.id,
            'title': 'Progress Validation Task',
            'assignee_user_id': self.member.id,
            'progress': 50.0,
        })
        self.assertEqual(task.progress, 50.0)

        with self.assertRaises(ValidationError):
            task.write({'progress': -5.0})

        with self.assertRaises(ValidationError):
            task.write({'progress': 105.0})

    def test_task_completion_sets_progress_and_status(self):
        """Test that action_mark_done sets status='done', state='1_done', and progress=100."""
        task = self.env['project.task'].with_user(self.pm).create({
            'project_id': self.project_a.id,
            'title': 'Completion Task',
            'assignee_user_id': self.member.id,
            'progress': 40.0,
        })
        task.action_start()
        self.assertEqual(task.status, 'in_progress')

        task.action_mark_done()
        self.assertEqual(task.status, 'done')
        self.assertEqual(task.state, '1_done')
        self.assertTrue(task.is_closed)
        self.assertEqual(task.progress, 100.0)

        with self.assertRaises(UserError):
            task.action_cancel()
