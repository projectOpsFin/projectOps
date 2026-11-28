# -*- coding: utf-8 -*-

import base64

from odoo.exceptions import AccessError, UserError
from odoo.tests.common import TransactionCase


class TestStep3Security(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env['res.partner'].create({
            'name': 'Step3 Security Client',
            'is_projectops_customer': True,
        })
        cls.user_ops = cls.env['res.users'].create({
            'name': 'Step3 Ops Manager',
            'login': 'step3_ops',
            'email': 'step3_ops@example.com',
            'hourly_cost_rate': 150.0,
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_manager').id])],
        })
        cls.user_pm = cls.env['res.users'].create({
            'name': 'Step3 PM',
            'login': 'step3_pm',
            'email': 'step3_pm@example.com',
            'hourly_cost_rate': 110.0,
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_project_manager').id])],
        })
        cls.user_finance = cls.env['res.users'].create({
            'name': 'Step3 Finance',
            'login': 'step3_finance',
            'email': 'step3_finance@example.com',
            'hourly_cost_rate': 95.0,
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_finance').id])],
        })
        cls.user_member_1 = cls.env['res.users'].create({
            'name': 'Step3 Member 1',
            'login': 'step3_member_1',
            'email': 'step3_m1@example.com',
            'hourly_cost_rate': 70.0,
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_team_member').id])],
        })
        cls.user_member_2 = cls.env['res.users'].create({
            'name': 'Step3 Member 2',
            'login': 'step3_member_2',
            'email': 'step3_m2@example.com',
            'hourly_cost_rate': 80.0,
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_team_member').id])],
        })
        cls.user_outsider = cls.env['res.users'].create({
            'name': 'Step3 Outsider',
            'login': 'step3_outsider',
            'email': 'step3_outsider@example.com',
            'hourly_cost_rate': 60.0,
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_team_member').id])],
        })

        cls.project = cls.env['project.project'].with_user(cls.user_pm).create({
            'project_code': 'PRJ-SEC3-01',
            'name': 'Step3 Security Project',
            'customer_id': cls.customer.id,
            'owner_user_id': cls.user_pm.id,
            'start_date': '2026-06-01',
            'contract_value': 250000.0,
            'cost_budget': 120000.0,
        })
        cls.env['projectops.assignment'].with_user(cls.user_pm).create([
            {'project_id': cls.project.id, 'user_id': cls.user_member_1.id, 'project_role': 'member'},
            {'project_id': cls.project.id, 'user_id': cls.user_member_2.id, 'project_role': 'member'},
        ])

        cls.sample_receipt = base64.b64encode(b'Receipt bytes')
        cls.wl_m1 = cls.env['account.analytic.line'].with_user(cls.user_member_1).create({
            'project_id': cls.project.id,
            'unit_amount': 4.0,
            'name': 'Member 1 draft worklog',
        })
        cls.wl_m2 = cls.env['account.analytic.line'].with_user(cls.user_member_2).create({
            'project_id': cls.project.id,
            'unit_amount': 6.0,
            'name': 'Member 2 draft worklog',
        })
        cls.exp_m1 = cls.env['hr.expense'].with_user(cls.user_member_1).create({
            'project_id': cls.project.id,
            'category': 'travel',
            'total_amount': 150.0,
            'name': 'Member 1 draft expense',
            'receipt_file': cls.sample_receipt,
        })
        cls.exp_m2 = cls.env['hr.expense'].with_user(cls.user_member_2).create({
            'project_id': cls.project.id,
            'category': 'meals',
            'total_amount': 65.0,
            'name': 'Member 2 draft expense',
            'receipt_file': cls.sample_receipt,
        })

    def test_team_member_isolation_on_worklogs_and_expenses(self):
        """Team Member sees/edits/deletes only own drafts on assigned projects."""
        self.wl_m1.with_user(self.user_member_1).write({'unit_amount': 4.5})
        self.exp_m1.with_user(self.user_member_1).write({'total_amount': 160.0})

        wl_search = self.env['account.analytic.line'].with_user(self.user_member_1).search([
            ('id', 'in', [self.wl_m1.id, self.wl_m2.id]),
        ])
        self.assertEqual(wl_search, self.wl_m1)

        exp_search = self.env['hr.expense'].with_user(self.user_member_1).search([
            ('id', 'in', [self.exp_m1.id, self.exp_m2.id]),
        ])
        self.assertEqual(exp_search, self.exp_m1)

        with self.assertRaises(AccessError):
            self.wl_m2.with_user(self.user_member_1).write({'unit_amount': 1.0})
        with self.assertRaises(AccessError):
            self.exp_m2.with_user(self.user_member_1).unlink()

        with self.assertRaises(AccessError):
            self.env['account.analytic.line'].with_user(self.user_outsider).create({
                'project_id': self.project.id,
                'unit_amount': 2.0,
                'name': 'Unauthorized',
            })
        with self.assertRaises(AccessError):
            self.env['hr.expense'].with_user(self.user_outsider).create({
                'project_id': self.project.id,
                'category': 'other',
                'total_amount': 10.0,
                'name': 'Unauthorized',
            })

    def test_team_member_cannot_edit_or_delete_after_submission(self):
        """Once submitted, Team Member can read own submission but cannot edit or delete it."""
        self.wl_m1.with_user(self.user_member_1).action_submit()
        self.exp_m1.with_user(self.user_member_1).action_submit()

        self.assertEqual(self.wl_m1.with_user(self.user_member_1).status, 'submitted')
        self.assertEqual(self.exp_m1.with_user(self.user_member_1).status, 'submitted')

        with self.assertRaises(UserError):
            self.wl_m1.with_user(self.user_member_1).write({'unit_amount': 9.0})
        with self.assertRaises(UserError):
            self.wl_m1.with_user(self.user_member_1).unlink()
        with self.assertRaises(AccessError):
            self.exp_m1.with_user(self.user_member_1).write({'total_amount': 999.0})
        with self.assertRaises(AccessError):
            self.exp_m1.with_user(self.user_member_1).unlink()

    def test_team_member_cannot_access_cost_rates(self):
        """BR-12 / SC-04: Team Members cannot read hourly_cost_rate or hourly_rate_snapshot."""
        with self.assertRaises(AccessError):
            _ = self.user_member_2.with_user(self.user_member_1).hourly_cost_rate
        with self.assertRaises(AccessError):
            _ = self.wl_m1.with_user(self.user_member_1).hourly_rate_snapshot

    def test_managers_and_finance_read_visibility(self):
        """PM, Operations Manager, and Finance can read all worklogs, expenses, and snapshots."""
        for user in (self.user_pm, self.user_ops, self.user_finance):
            wls = self.env['account.analytic.line'].with_user(user).search([
                ('id', 'in', [self.wl_m1.id, self.wl_m2.id]),
            ])
            self.assertEqual(len(wls), 2)
            self.assertEqual(self.wl_m1.with_user(user).hourly_rate_snapshot, 70.0)

            exps = self.env['hr.expense'].with_user(user).search([
                ('id', 'in', [self.exp_m1.id, self.exp_m2.id]),
            ])
            self.assertEqual(len(exps), 2)

        with self.assertRaises(AccessError):
            self.wl_m1.with_user(self.user_finance).write({'unit_amount': 10.0})
        with self.assertRaises(AccessError):
            self.exp_m1.with_user(self.user_finance).write({'total_amount': 500.0})
        with self.assertRaises(AccessError):
            self.env['account.analytic.line'].with_user(self.user_finance).create({
                'project_id': self.project.id,
                'unit_amount': 1.0,
                'name': 'Finance worklog',
            })
