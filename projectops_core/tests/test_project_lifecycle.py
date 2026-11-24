# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestProjectLifecycle(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env['res.partner'].create({
            'name': 'Lifecycle Test Client',
            'is_projectops_customer': True,
        })
        cls.owner = cls.env['res.users'].create({
            'name': 'Lifecycle Owner',
            'login': 'lifecycle_owner',
            'email': 'lifecycle_owner@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_project_manager').id])],
        })
        cls.project = cls.env['project.project'].create({
            'project_code': 'PRJ-LIFECYCLE-01',
            'name': 'Lifecycle Project',
            'customer_id': cls.customer.id,
            'owner_user_id': cls.owner.id,
            'start_date': '2026-05-01',
            'end_date': '2026-11-01',
            'contract_value': 180000.0,
            'cost_budget': 110000.0,
        })

    def test_project_lifecycle_transitions(self):
        """Test the lifecycle flow: draft -> in_progress -> completed."""
        # Initial state is draft
        self.assertEqual(self.project.state, 'draft')

        # Activate project
        self.project.action_activate()
        self.assertEqual(self.project.state, 'in_progress')

        # Cannot activate an in-progress project
        with self.assertRaises(UserError):
            self.project.action_activate()

        # Complete project
        self.project.action_complete()
        self.assertEqual(self.project.state, 'completed')

        # Cannot complete an already completed project
        with self.assertRaises(UserError):
            self.project.action_complete()

    def test_cannot_complete_draft_project(self):
        """Test that a draft project cannot be marked completed directly."""
        with self.assertRaises(UserError):
            self.project.action_complete()
