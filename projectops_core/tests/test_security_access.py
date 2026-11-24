# -*- coding: utf-8 -*-

from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase


class TestSecurityAccess(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env['res.partner'].create({
            'name': 'Security Test Partner',
            'is_projectops_customer': True,
        })

        # Role 1: Owner / Operations Manager
        cls.user_operations_manager = cls.env['res.users'].create({
            'name': 'Ops Manager User',
            'login': 'ops_manager_user',
            'email': 'ops_mgr@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_manager').id])],
        })

        # Role 2: Project Manager
        cls.user_pm = cls.env['res.users'].create({
            'name': 'PM User',
            'login': 'pm_user',
            'email': 'pm@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_project_manager').id])],
        })

        # Role 3: Finance Officer
        cls.user_finance = cls.env['res.users'].create({
            'name': 'Finance User',
            'login': 'finance_user',
            'email': 'finance@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_finance').id])],
        })

        # Role 4: Team Member
        cls.user_member = cls.env['res.users'].create({
            'name': 'Member User',
            'login': 'member_user',
            'email': 'member@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_team_member').id])],
        })

        # Another unassigned team member
        cls.user_unassigned_member = cls.env['res.users'].create({
            'name': 'Unassigned Member User',
            'login': 'unassigned_member_user',
            'email': 'unassigned@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_team_member').id])],
        })

        # Project created by PM
        cls.project = cls.env['project.project'].with_user(cls.user_pm).create({
            'project_code': 'PRJ-SEC-01',
            'name': 'Security Controlled Project',
            'customer_id': cls.customer.id,
            'owner_user_id': cls.user_pm.id,
            'start_date': '2026-06-01',
            'end_date': '2026-12-01',
            'contract_value': 300000.0,
            'cost_budget': 180000.0,
        })

        # Assign user_member to project
        cls.env['projectops.assignment'].with_user(cls.user_pm).create({
            'project_id': cls.project.id,
            'user_id': cls.user_member.id,
            'project_role': 'member',
        })

    def test_pm_can_create_and_edit_project(self):
        """Verify that a Project Manager can create and edit projects."""
        project = self.project.with_user(self.user_pm)
        self.assertEqual(project.name, 'Security Controlled Project')
        project.write({'name': 'Updated PM Project Name'})
        self.assertEqual(project.name, 'Updated PM Project Name')

    def test_finance_can_read_project_and_financials(self):
        """Verify that Finance Officer can read projects and financial fields."""
        project = self.project.with_user(self.user_finance)
        self.assertEqual(project.contract_value, 300000.0)
        self.assertEqual(project.cost_budget, 180000.0)

    def test_finance_cannot_create_project(self):
        """Verify that Finance Officer cannot create projects."""
        with self.assertRaises(AccessError):
            self.env['project.project'].with_user(self.user_finance).create({
                'project_code': 'PRJ-FIN-FAIL',
                'name': 'Unauthorized Finance Project',
                'customer_id': self.customer.id,
                'owner_user_id': self.user_pm.id,
                'start_date': '2026-01-01',
                'contract_value': 10000.0,
                'cost_budget': 5000.0,
            })

    def test_assigned_member_can_read_assigned_project(self):
        """Verify that assigned team member can read the project they are assigned to."""
        project = self.project.with_user(self.user_member)
        self.assertEqual(project.name, 'Security Controlled Project')

    def test_team_member_cannot_edit_project(self):
        """Verify that team member cannot modify project details."""
        project = self.project.with_user(self.user_member)
        with self.assertRaises(AccessError):
            project.write({'name': 'Hacked by Team Member'})

    def test_team_member_cannot_access_commercial_fields(self):
        """Verify BR-12 / SC-04: Team members must not access commercial data (contract_value, cost_budget)."""
        project = self.project.with_user(self.user_member)
        with self.assertRaises(AccessError):
            _ = project.contract_value

        with self.assertRaises(AccessError):
            _ = project.cost_budget

    def test_unassigned_member_cannot_see_project(self):
        """Verify record rule: unassigned team member cannot see or read project records."""
        project_ids = self.env['project.project'].with_user(self.user_unassigned_member).search([
            ('id', '=', self.project.id)
        ])
        self.assertEqual(len(project_ids), 0)
