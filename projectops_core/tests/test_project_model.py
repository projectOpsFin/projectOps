# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestProjectModel(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env['res.partner'].create({
            'name': 'Ethiopian Tech Enterprise',
            'email': 'info@etech.et',
            'billing_address': 'Addis Ababa, Ethiopia',
            'is_projectops_customer': True,
        })
        cls.owner = cls.env['res.users'].create({
            'name': 'Project Owner Alice',
            'login': 'owner_alice_test',
            'email': 'alice@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_project_manager').id])],
        })

    def test_valid_project_creation(self):
        """Test creating a valid project with required fields and defaults."""
        project = self.env['project.project'].create({
            'project_code': 'PRJ-2026-VAL-01',
            'name': 'Validation Project',
            'customer_id': self.customer.id,
            'owner_user_id': self.owner.id,
            'start_date': '2026-03-01',
            'end_date': '2026-09-01',
            'contract_value': 250000.0,
            'cost_budget': 150000.0,
        })
        self.assertEqual(project.state, 'draft')
        self.assertEqual(project.project_code, 'PRJ-2026-VAL-01')
        self.assertEqual(project.partner_id, self.customer)
        self.assertEqual(project.user_id, self.owner)
        self.assertEqual(str(project.date_start), '2026-03-01')
        self.assertEqual(str(project.date), '2026-09-01')

    def test_duplicate_project_code_rejected(self):
        """Test that duplicate project codes are strictly rejected."""
        self.env['project.project'].create({
            'project_code': 'PRJ-UNIQUE-01',
            'name': 'First Unique Project',
            'customer_id': self.customer.id,
            'owner_user_id': self.owner.id,
            'start_date': '2026-01-01',
            'end_date': '2026-05-01',
            'contract_value': 50000.0,
            'cost_budget': 30000.0,
        })
        with self.assertRaises(ValidationError):
            self.env['project.project'].create({
                'project_code': 'PRJ-UNIQUE-01',
                'name': 'Duplicate Code Project',
                'customer_id': self.customer.id,
                'owner_user_id': self.owner.id,
                'start_date': '2026-02-01',
                'end_date': '2026-06-01',
                'contract_value': 80000.0,
                'cost_budget': 40000.0,
            })

    def test_end_date_earlier_than_start_date_rejected(self):
        """Test that planned end date cannot be earlier than start date."""
        with self.assertRaises(ValidationError):
            self.env['project.project'].create({
                'project_code': 'PRJ-INVALID-DATE',
                'name': 'Invalid Date Project',
                'customer_id': self.customer.id,
                'owner_user_id': self.owner.id,
                'start_date': '2026-06-01',
                'end_date': '2026-05-01',
                'contract_value': 50000.0,
                'cost_budget': 30000.0,
            })

    def test_negative_financial_values_rejected(self):
        """Test that contract value and cost budget must be non-negative."""
        with self.assertRaises(ValidationError):
            self.env['project.project'].create({
                'project_code': 'PRJ-NEG-VAL',
                'name': 'Negative Value Project',
                'customer_id': self.customer.id,
                'owner_user_id': self.owner.id,
                'start_date': '2026-01-01',
                'contract_value': -100.0,
                'cost_budget': 5000.0,
            })

        with self.assertRaises(ValidationError):
            self.env['project.project'].create({
                'project_code': 'PRJ-NEG-BUDGET',
                'name': 'Negative Budget Project',
                'customer_id': self.customer.id,
                'owner_user_id': self.owner.id,
                'start_date': '2026-01-01',
                'contract_value': 10000.0,
                'cost_budget': -500.0,
            })

    def test_missing_customer_rejected(self):
        """Test that a project cannot be created without a customer."""
        with self.assertRaises(Exception):
            self.env['project.project'].create({
                'project_code': 'PRJ-NO-CUST',
                'name': 'No Customer Project',
                'owner_user_id': self.owner.id,
                'start_date': '2026-01-01',
                'contract_value': 10000.0,
                'cost_budget': 5000.0,
            })
