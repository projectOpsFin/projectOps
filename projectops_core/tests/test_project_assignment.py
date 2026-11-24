# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestProjectAssignment(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env['res.partner'].create({
            'name': 'Assignment Test Client',
            'is_projectops_customer': True,
        })
        cls.owner = cls.env['res.users'].create({
            'name': 'Assignment Owner',
            'login': 'assignment_owner',
            'email': 'assignment_owner@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_project_manager').id])],
        })
        cls.member1 = cls.env['res.users'].create({
            'name': 'Dev Member 1',
            'login': 'dev_member_1',
            'email': 'dev1@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_team_member').id])],
        })
        cls.member2 = cls.env['res.users'].create({
            'name': 'QA Member 2',
            'login': 'qa_member_2',
            'email': 'qa2@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_team_member').id])],
        })
        cls.project = cls.env['project.project'].create({
            'project_code': 'PRJ-ASSIGN-01',
            'name': 'Assignment Project',
            'customer_id': cls.customer.id,
            'owner_user_id': cls.owner.id,
            'start_date': '2026-04-01',
            'end_date': '2026-10-01',
            'contract_value': 120000.0,
            'cost_budget': 75000.0,
        })

    def test_assign_team_members(self):
        """Test assigning team members with specific roles to a project."""
        assignment1 = self.env['projectops.assignment'].create({
            'project_id': self.project.id,
            'user_id': self.member1.id,
            'project_role': 'lead',
            'start_date': '2026-04-01',
            'end_date': '2026-10-01',
        })
        assignment2 = self.env['projectops.assignment'].create({
            'project_id': self.project.id,
            'user_id': self.member2.id,
            'project_role': 'qa',
            'start_date': '2026-05-01',
        })

        self.assertEqual(len(self.project.assignment_ids), 2)
        self.assertIn(self.member1, self.project.assigned_user_ids)
        self.assertIn(self.member2, self.project.assigned_user_ids)
        self.assertEqual(assignment1.project_role, 'lead')
        self.assertEqual(assignment2.project_role, 'qa')

    def test_duplicate_assignment_prevented(self):
        """Test that assigning the same user twice to a project raises ValidationError."""
        self.env['projectops.assignment'].create({
            'project_id': self.project.id,
            'user_id': self.member1.id,
            'project_role': 'member',
        })

        with self.assertRaises(ValidationError):
            self.env['projectops.assignment'].create({
                'project_id': self.project.id,
                'user_id': self.member1.id,
                'project_role': 'lead',
            })

    def test_invalid_assignment_dates_rejected(self):
        """Test that assignment end date cannot be earlier than its start date."""
        with self.assertRaises(ValidationError):
            self.env['projectops.assignment'].create({
                'project_id': self.project.id,
                'user_id': self.member1.id,
                'project_role': 'member',
                'start_date': '2026-08-01',
                'end_date': '2026-07-01',
            })
