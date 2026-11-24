# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestCustomerManagement(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env['res.partner'].create({
            'name': 'Acme Services Corp',
            'email': 'contact@acmeservices.com',
            'phone': '+251 911 000 111',
            'billing_address': 'Bole Subcity, House 456, Addis Ababa, Ethiopia',
            'is_projectops_customer': True,
        })

    def test_customer_creation(self):
        """Verify that an authorized user can create and view customer records."""
        self.assertEqual(self.customer.name, 'Acme Services Corp')
        self.assertEqual(self.customer.email, 'contact@acmeservices.com')
        self.assertEqual(self.customer.phone, '+251 911 000 111')
        self.assertEqual(self.customer.billing_address, 'Bole Subcity, House 456, Addis Ababa, Ethiopia')
        self.assertTrue(self.customer.is_projectops_customer)
        self.assertEqual(self.customer.projectops_project_count, 0)

    def test_customer_project_linking(self):
        """Verify that projects correctly increment the customer's project count."""
        project = self.env['project.project'].create({
            'project_code': 'PRJ-TEST-CUST-01',
            'name': 'Customer Test Project',
            'customer_id': self.customer.id,
            'owner_user_id': self.env.user.id,
            'start_date': '2026-01-01',
            'end_date': '2026-06-30',
            'contract_value': 100000.0,
            'cost_budget': 60000.0,
        })
        self.assertIn(project, self.customer.projectops_project_ids)
        self.assertEqual(self.customer.projectops_project_count, 1)
