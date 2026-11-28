# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

EXPENSE_STATE_TO_STATUS = {
    'draft': 'draft',
    'submitted': 'submitted',
    'approved': 'approved',
    'posted': 'approved',
    'in_payment': 'approved',
    'paid': 'approved',
    'refused': 'rejected',
}


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        ondelete='cascade',
        index=True,
        tracking=True,
        help='Project to which this expense applies.',
    )
    submitter_user_id = fields.Many2one(
        'res.users',
        string='Submitted By',
        compute='_compute_submitter_user_id',
        store=True,
        readonly=False,
        index=True,
        tracking=True,
        help='User who incurred and submitted the expense.',
    )
    category = fields.Selection(
        selection=[
            ('travel', 'Travel'),
            ('accommodation', 'Accommodation'),
            ('meals', 'Meals & Subsistence'),
            ('software', 'Software & Subscriptions'),
            ('hardware', 'Equipment & Hardware'),
            ('materials', 'Materials & Supplies'),
            ('other', 'Other'),
        ],
        string='ProjectOps Category',
        required=True,
        default='other',
        tracking=True,
        help='Standardized ProjectOps expense category.',
    )
    receipt_file = fields.Binary(
        string='Receipt File',
        attachment=True,
        help='Optional direct receipt file upload alongside chatter attachments.',
    )
    receipt_filename = fields.Char(
        string='Receipt Filename',
    )
    status = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        string='ProjectOps Status',
        required=True,
        default='draft',
        copy=False,
        tracking=True,
        index=True,
        help='Current ProjectOps submission and approval status of the expense.',
    )

    @api.depends('employee_id.user_id')
    def _compute_submitter_user_id(self):
        for expense in self:
            if expense.employee_id.user_id:
                expense.submitter_user_id = expense.employee_id.user_id
            elif not expense.submitter_user_id:
                expense.submitter_user_id = self.env.user

    @api.constrains('project_id')
    def _check_project_required(self):
        for expense in self:
            if not expense.project_id:
                raise ValidationError("Every ProjectOps expense must belong to a valid project.")

    @api.constrains('total_amount', 'total_amount_currency')
    def _check_amount_positive_val(self):
        for expense in self:
            effective_amount = expense.total_amount_currency or expense.total_amount
            if effective_amount <= 0.0:
                raise ValidationError("Expense amount must be strictly positive.")

    @api.constrains('name')
    def _check_name_not_empty(self):
        for expense in self:
            if not expense.name or not expense.name.strip():
                raise ValidationError("Expense description cannot be empty.")

    @api.constrains('project_id', 'submitter_user_id', 'employee_id')
    def _check_submitter_authorized(self):
        for expense in self:
            submitter = expense.submitter_user_id or expense.employee_id.user_id
            if not expense.project_id or not submitter:
                continue
            expense._validate_submitter_on_project(submitter, expense.project_id)

    def _validate_submitter_on_project(self, user, project):
        project_sudo = project.sudo()
        is_owner = project_sudo.owner_user_id == user
        is_assigned = user in project_sudo.assigned_user_ids
        is_pm = user.has_group('projectops_core.group_projectops_project_manager')
        if not (is_owner or is_assigned or is_pm):
            raise ValidationError("The submitter must be assigned to or authorized on the selected project.")

    def _has_receipt(self):
        self.ensure_one()
        if self.receipt_file or self.message_main_attachment_id or self.attachment_ids:
            return True
        attachment_count = self.env['ir.attachment'].sudo().search_count([
            ('res_model', '=', 'hr.expense'),
            ('res_id', '=', self.id),
        ])
        return attachment_count > 0

    @api.model
    def _ensure_employee_for_user(self, user):
        """Return an hr.employee for user, creating one if none exists."""
        employee = user.sudo().employee_id
        if employee:
            return employee
        return self.env['hr.employee'].sudo().create({
            'name': user.name,
            'user_id': user.id,
            'company_id': user.company_id.id or self.env.company.id,
        })

    @api.model_create_multi
    def create(self, vals_list):
        allow_transition = self.env.context.get('_projectops_workflow_transition')
        is_manager = self.env.user.has_group('projectops_core.group_projectops_project_manager')
        cleaned_vals_list = []
        for vals in vals_list:
            vals_copy = dict(vals)
            if not allow_transition and vals_copy.get('status') not in (None, 'draft'):
                raise UserError("New expenses must start in Draft status.")
            if not vals_copy.get('project_id'):
                raise ValidationError("Every ProjectOps expense must belong to a valid project.")
            if 'total_amount' in vals_copy and vals_copy['total_amount'] <= 0.0:
                raise ValidationError("Expense amount must be strictly positive.")
            if 'total_amount_currency' in vals_copy and vals_copy['total_amount_currency'] <= 0.0:
                raise ValidationError("Expense amount must be strictly positive.")
            if 'name' in vals_copy and (not vals_copy['name'] or not str(vals_copy['name']).strip()):
                raise ValidationError("Expense description cannot be empty.")

            if not vals_copy.get('employee_id'):
                submitter_id = vals_copy.get('submitter_user_id') or self.env.user.id
                submitter = self.env['res.users'].sudo().browse(submitter_id)
                vals_copy['employee_id'] = self._ensure_employee_for_user(submitter).id
                vals_copy.setdefault('submitter_user_id', submitter_id)

            if not self.env.su and not is_manager:
                project = self.env['project.project'].sudo().browse(vals_copy['project_id'])
                if project.owner_user_id != self.env.user and self.env.user not in project.assigned_user_ids:
                    raise AccessError("You can only create expenses on projects you are assigned to.")
            cleaned_vals_list.append(vals_copy)
        return super().create(cleaned_vals_list)

    def write(self, vals):
        if not self.env.su:
            self.check_access('write')
        allow_transition = self.env.context.get('_projectops_workflow_transition')
        if 'total_amount' in vals and vals['total_amount'] <= 0.0:
            raise ValidationError("Expense amount must be strictly positive.")
        if 'total_amount_currency' in vals and vals['total_amount_currency'] <= 0.0:
            raise ValidationError("Expense amount must be strictly positive.")
        if 'name' in vals and (not vals['name'] or not str(vals['name']).strip()):
            raise ValidationError("Expense description cannot be empty.")
        if not allow_transition:
            if 'status' in vals:
                raise UserError("Expense status must be changed through workflow actions.")
            for record in self:
                if record.status != 'draft':
                    raise UserError("Only draft expenses can be modified.")
        return super().write(vals)

    @api.ondelete(at_uninstall=False)
    def _unlink_only_draft_expenses(self):
        if not self.env.su:
            self.check_access('unlink')
        for record in self:
            if record.status != 'draft':
                raise UserError("Only draft expenses can be deleted.")

    def action_submit(self):
        self.check_access('write')
        is_manager = self.env.user.has_group('projectops_core.group_projectops_project_manager')
        for expense in self:
            if expense.status != 'draft':
                raise UserError("Only draft expenses can be submitted.")
            submitter = expense.submitter_user_id or expense.employee_id.user_id
            if not is_manager and submitter != self.env.user:
                raise AccessError("You can only submit your own expenses.")
            effective_amount = expense.total_amount_currency or expense.total_amount
            if effective_amount <= 0.0:
                raise ValidationError("Expense amount must be strictly positive.")
            if not expense.name or not expense.name.strip():
                raise ValidationError("Expense description cannot be empty.")
            if submitter:
                expense._validate_submitter_on_project(submitter, expense.project_id)
            if not expense._has_receipt():
                raise ValidationError("A supporting receipt attachment is required before submitting an expense.")

            expense.sudo().with_context(_projectops_workflow_transition=True).write({
                'status': 'submitted',
                'approval_state': 'submitted',
            })
