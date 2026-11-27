# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestMilestoneModel(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env['res.partner'].create({
            'name': 'Milestone Test Client',
            'is_projectops_customer': True,
        })
        cls.owner = cls.env['res.users'].create({
            'name': 'Milestone Owner',
            'login': 'milestone_owner_test',
            'email': 'milestone_owner@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_project_manager').id])],
        })
        cls.project = cls.env['project.project'].create({
            'project_code': 'PRJ-MS-01',
            'name': 'Milestone Project',
            'customer_id': cls.customer.id,
            'owner_user_id': cls.owner.id,
            'start_date': '2026-04-01',
            'end_date': '2026-10-01',
            'contract_value': 100000.0,
            'cost_budget': 60000.0,
        })

    def test_milestone_creation_and_project_link(self):
        """Test creating a valid milestone linked to a project."""
        ms = self.env['projectops.milestone'].with_user(self.owner).create({
            'project_id': self.project.id,
            'title': 'Phase 1 Delivery',
            'description': 'Initial architecture and setup',
            'due_date': '2026-06-01',
            'sequence': 1,
        })
        self.assertEqual(ms.status, 'planned')
        self.assertEqual(ms.project_id, self.project)
        self.assertIn(ms, self.project.projectops_milestone_ids)
        self.assertEqual(self.project.projectops_milestone_count, 1)

    def test_milestone_requires_valid_project(self):
        """Test that a milestone cannot be created without a project."""
        with self.assertRaises(ValidationError):
            self.env['projectops.milestone'].create({
                'title': 'Orphan Milestone',
            })

    def test_milestone_title_and_sequence_validation(self):
        """Test that blank title and negative sequence are rejected."""
        with self.assertRaises(ValidationError):
            self.env['projectops.milestone'].create({
                'project_id': self.project.id,
                'title': '   ',
            })
        with self.assertRaises(ValidationError):
            self.env['projectops.milestone'].create({
                'project_id': self.project.id,
                'title': 'Negative Seq',
                'sequence': -1,
            })

    def test_milestone_status_transitions(self):
        """Test milestone lifecycle transitions."""
        ms = self.env['projectops.milestone'].with_user(self.owner).create({
            'project_id': self.project.id,
            'title': 'Beta Release',
        })
        self.assertEqual(ms.status, 'planned')
        ms.action_start()
        self.assertEqual(ms.status, 'in_progress')
        ms.action_complete()
        self.assertEqual(ms.status, 'completed')
        with self.assertRaises(UserError):
            ms.action_cancel()
        ms.action_reopen()
        self.assertEqual(ms.status, 'planned')
        ms.action_cancel()
        self.assertEqual(ms.status, 'cancelled')
