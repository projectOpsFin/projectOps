# -*- coding: utf-8 -*-

from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase


class TestStep2Security(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env['res.partner'].create({
            'name': 'Step2 Security Client',
            'is_projectops_customer': True,
        })
        cls.user_pm = cls.env['res.users'].create({
            'name': 'Step2 PM',
            'login': 'step2_pm',
            'email': 'step2_pm@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_project_manager').id])],
        })
        cls.user_finance = cls.env['res.users'].create({
            'name': 'Step2 Finance',
            'login': 'step2_finance',
            'email': 'step2_finance@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_finance').id])],
        })
        cls.user_member_1 = cls.env['res.users'].create({
            'name': 'Step2 Member 1',
            'login': 'step2_member_1',
            'email': 'step2_m1@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_team_member').id])],
        })
        cls.user_member_2 = cls.env['res.users'].create({
            'name': 'Step2 Member 2',
            'login': 'step2_member_2',
            'email': 'step2_m2@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_team_member').id])],
        })
        cls.user_outsider = cls.env['res.users'].create({
            'name': 'Step2 Outsider',
            'login': 'step2_outsider',
            'email': 'step2_outsider@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_team_member').id])],
        })

        cls.project = cls.env['project.project'].with_user(cls.user_pm).create({
            'project_code': 'PRJ-SEC2-01',
            'name': 'Step2 Security Project',
            'customer_id': cls.customer.id,
            'owner_user_id': cls.user_pm.id,
            'start_date': '2026-06-01',
            'contract_value': 200000.0,
            'cost_budget': 100000.0,
        })
        cls.env['projectops.assignment'].with_user(cls.user_pm).create([
            {'project_id': cls.project.id, 'user_id': cls.user_member_1.id, 'project_role': 'member'},
            {'project_id': cls.project.id, 'user_id': cls.user_member_2.id, 'project_role': 'member'},
        ])
        cls.milestone = cls.env['projectops.milestone'].with_user(cls.user_pm).create({
            'project_id': cls.project.id,
            'title': 'Secured Milestone',
        })
        cls.task_m1 = cls.env['project.task'].with_user(cls.user_pm).create({
            'project_id': cls.project.id,
            'projectops_milestone_id': cls.milestone.id,
            'title': 'Member 1 Task',
            'assignee_user_id': cls.user_member_1.id,
            'progress': 10.0,
        })
        cls.task_m2 = cls.env['project.task'].with_user(cls.user_pm).create({
            'project_id': cls.project.id,
            'projectops_milestone_id': cls.milestone.id,
            'title': 'Member 2 Task',
            'assignee_user_id': cls.user_member_2.id,
            'progress': 20.0,
        })

    def test_team_member_can_update_own_task_progress_only(self):
        """Team member can update progress/status on own task, not restricted fields or others' tasks."""
        own_task = self.task_m1.with_user(self.user_member_1)
        own_task.write({'progress': 60.0})
        self.assertEqual(own_task.progress, 60.0)
        own_task.action_mark_done()
        self.assertEqual(own_task.status, 'done')

        # Cannot modify restricted fields on own task
        with self.assertRaises(AccessError):
            own_task.write({'assignee_user_id': self.user_member_2.id})
        with self.assertRaises(AccessError):
            own_task.write({'title': 'Renamed by Member'})

        # Cannot modify another member's task
        other_task = self.task_m2.with_user(self.user_member_1)
        with self.assertRaises(AccessError):
            other_task.write({'progress': 90.0})

    def test_team_member_cannot_create_task_or_modify_milestone(self):
        """Team member cannot create tasks or modify/create milestones."""
        with self.assertRaises(AccessError):
            self.env['project.task'].with_user(self.user_member_1).create({
                'project_id': self.project.id,
                'title': 'Unauthorized Task',
            })
        with self.assertRaises(AccessError):
            self.milestone.with_user(self.user_member_1).write({'title': 'Hacked Milestone'})
        with self.assertRaises(AccessError):
            self.milestone.with_user(self.user_member_1).action_start()

    def test_unassigned_user_cannot_see_milestones_or_tasks(self):
        """Unassigned team member cannot read milestones or tasks of unassigned projects."""
        ms_found = self.env['projectops.milestone'].with_user(self.user_outsider).search([
            ('id', '=', self.milestone.id),
        ])
        self.assertEqual(len(ms_found), 0)

        tasks_found = self.env['project.task'].with_user(self.user_outsider).search([
            ('id', 'in', [self.task_m1.id, self.task_m2.id]),
        ])
        self.assertEqual(len(tasks_found), 0)

    def test_finance_is_read_only_on_milestones_and_tasks(self):
        """Finance Officer can read milestones and tasks but cannot modify or create them."""
        self.assertEqual(self.milestone.with_user(self.user_finance).title, 'Secured Milestone')
        self.assertEqual(self.task_m1.with_user(self.user_finance).title, 'Member 1 Task')

        with self.assertRaises(AccessError):
            self.milestone.with_user(self.user_finance).write({'title': 'Finance Edit'})
        with self.assertRaises(AccessError):
            self.task_m1.with_user(self.user_finance).write({'progress': 99.0})
        with self.assertRaises(AccessError):
            self.env['project.task'].with_user(self.user_finance).create({
                'project_id': self.project.id,
                'title': 'Finance Task',
            })
