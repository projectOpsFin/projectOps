# -*- coding: utf-8 -*-

import base64

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestExpenseModel(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env['res.partner'].create({
            'name': 'Expense Test Client',
            'is_projectops_customer': True,
        })
        cls.user_pm = cls.env['res.users'].create({
            'name': 'Expense PM',
            'login': 'expense_pm',
            'email': 'expense_pm@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_project_manager').id])],
        })
        cls.user_member = cls.env['res.users'].create({
            'name': 'Expense Member',
            'login': 'expense_member',
            'email': 'expense_member@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_team_member').id])],
        })
        cls.user_unassigned = cls.env['res.users'].create({
            'name': 'Expense Outsider',
            'login': 'expense_outsider',
            'email': 'expense_outsider@example.com',
            'group_ids': [(6, 0, [cls.env.ref('projectops_core.group_projectops_team_member').id])],
        })

        cls.project = cls.env['project.project'].with_user(cls.user_pm).create({
            'project_code': 'PRJ-EXP-01',
            'name': 'Expense Project',
            'customer_id': cls.customer.id,
            'owner_user_id': cls.user_pm.id,
            'start_date': '2026-06-01',
            'contract_value': 100000.0,
            'cost_budget': 60000.0,
        })
        cls.env['projectops.assignment'].with_user(cls.user_pm).create({
            'project_id': cls.project.id,
            'user_id': cls.user_member.id,
            'project_role': 'member',
        })
        cls.sample_receipt = base64.b64encode(b'Sample PDF receipt content')

    def test_create_and_submit_expense_with_receipt_file(self):
        """hr.expense links to project and transitions draft -> submitted when receipt_file is present."""
        expense = self.env['hr.expense'].with_user(self.user_member).create({
            'project_id': self.project.id,
            'date': '2026-06-12',
            'category': 'travel',
            'total_amount': 450.0,
            'name': 'Client site taxi fare',
            'receipt_file': self.sample_receipt,
            'receipt_filename': 'taxi_receipt.pdf',
        })
        self.assertEqual(expense.status, 'draft')
        self.assertIn(expense, self.project.expense_ids)
        self.assertEqual(self.project.expense_count, 1)

        expense.action_submit()
        self.assertEqual(expense.status, 'submitted')
        self.assertEqual(expense.approval_state, 'submitted')

    def test_submit_expense_with_ir_attachment(self):
        """Expense can also be submitted when a supporting ir.attachment is linked."""
        expense = self.env['hr.expense'].with_user(self.user_member).create({
            'project_id': self.project.id,
            'category': 'software',
            'total_amount': 99.0,
            'name': 'Cloud test tool subscription',
        })
        # Without receipt, submission fails
        with self.assertRaises(ValidationError):
            expense.action_submit()

        # Attach via native ir.attachment
        self.env['ir.attachment'].with_user(self.user_member).create({
            'name': 'invoice.pdf',
            'datas': self.sample_receipt,
            'res_model': 'hr.expense',
            'res_id': expense.id,
        })
        expense.action_submit()
        self.assertEqual(expense.status, 'submitted')

    def test_expense_validation_constraints(self):
        """Validate positive amount, non-empty description, project, and submitter assignment."""
        with self.assertRaises(ValidationError):
            self.env['hr.expense'].with_user(self.user_member).create({
                'project_id': self.project.id,
                'category': 'meals',
                'total_amount': 0.0,
                'name': 'Zero amount',
            })
        with self.assertRaises(ValidationError):
            self.env['hr.expense'].with_user(self.user_member).create({
                'project_id': self.project.id,
                'category': 'meals',
                'total_amount': -50.0,
                'name': 'Negative amount',
            })
        with self.assertRaises(ValidationError):
            self.env['hr.expense'].with_user(self.user_member).create({
                'project_id': self.project.id,
                'category': 'meals',
                'total_amount': 25.0,
                'name': '   ',
            })
        with self.assertRaises(ValidationError):
            self.env['hr.expense'].sudo().create({
                'project_id': self.project.id,
                'submitter_user_id': self.user_unassigned.id,
                'category': 'other',
                'total_amount': 25.0,
                'name': 'Unassigned submitter',
            })

    def test_expense_lock_after_submission(self):
        """Submitted expenses cannot be edited, deleted, or resubmitted."""
        expense = self.env['hr.expense'].with_user(self.user_member).create({
            'project_id': self.project.id,
            'category': 'materials',
            'total_amount': 120.0,
            'name': 'Cables',
            'receipt_file': self.sample_receipt,
        })
        expense.action_submit()

        with self.assertRaises(UserError):
            expense.sudo().write({'total_amount': 200.0})
        with self.assertRaises(UserError):
            expense.sudo().unlink()
        with self.assertRaises(UserError):
            expense.action_submit()
        with self.assertRaises(UserError):
            expense.sudo().write({'status': 'approved'})
