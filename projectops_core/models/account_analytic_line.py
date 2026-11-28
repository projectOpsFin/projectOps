# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    hourly_rate_snapshot = fields.Monetary(
        string='Hourly Rate Snapshot',
        currency_field='currency_id',
        readonly=True,
        copy=False,
        default=0.0,
        groups='projectops_core.group_projectops_project_manager,projectops_core.group_projectops_finance',
        help='Historical hourly cost rate captured at creation/submission.',
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
        index=True,
        help='Current submission and approval status of the worklog.',
    )

    @api.constrains('unit_amount', 'project_id')
    def _check_worklog_hours_positive(self):
        for line in self:
            if line.project_id and line.unit_amount <= 0.0:
                raise ValidationError("Worklog hours must be strictly positive.")

    @api.constrains('name', 'project_id')
    def _check_worklog_description_not_empty(self):
        for line in self:
            if line.project_id and (not line.name or not line.name.strip()):
                raise ValidationError("Worklog description cannot be empty.")

    @api.constrains('project_id', 'task_id')
    def _check_worklog_task_same_project(self):
        for line in self:
            if line.project_id and line.task_id and line.task_id.project_id != line.project_id:
                raise ValidationError("The selected task must belong to the same project as the worklog.")

    @api.constrains('project_id', 'user_id')
    def _check_worklog_submitter_authorized(self):
        for line in self:
            if not line.project_id or not line.user_id:
                continue
            line._validate_submitter_on_project(line.user_id, line.project_id)

    def _validate_submitter_on_project(self, user, project):
        project_sudo = project.sudo()
        is_owner = project_sudo.owner_user_id == user
        is_assigned = user in project_sudo.assigned_user_ids
        is_pm = user.has_group('projectops_core.group_projectops_project_manager')
        if not (is_owner or is_assigned or is_pm):
            raise ValidationError("The submitter must be assigned to or authorized on the selected project.")

    @api.model_create_multi
    def create(self, vals_list):
        allow_snapshot = self.env.context.get('_projectops_allow_snapshot_write')
        allow_transition = self.env.context.get('_projectops_workflow_transition')
        is_manager = self.env.user.has_group('projectops_core.group_projectops_project_manager')
        cleaned_vals_list = []
        for vals in vals_list:
            vals_copy = dict(vals)
            if vals_copy.get('project_id'):
                if not allow_snapshot and 'hourly_rate_snapshot' in vals_copy:
                    raise UserError("Hourly rate snapshot is captured automatically and cannot be set manually.")
                if not allow_transition and vals_copy.get('status') not in (None, 'draft'):
                    raise UserError("New worklogs must start in Draft status.")
                if 'unit_amount' in vals_copy and (vals_copy['unit_amount'] is False or vals_copy['unit_amount'] <= 0.0):
                    raise ValidationError("Worklog hours must be strictly positive.")
                if 'name' in vals_copy and (not vals_copy['name'] or not str(vals_copy['name']).strip()):
                    raise ValidationError("Worklog description cannot be empty.")
                if not self.env.su and not is_manager:
                    project = self.env['project.project'].sudo().browse(vals_copy['project_id'])
                    if project.owner_user_id != self.env.user and self.env.user not in project.assigned_user_ids:
                        raise AccessError("You can only create worklogs on projects you are assigned to.")
                if 'user_id' not in vals_copy and not vals_copy.get('employee_id'):
                    vals_copy['user_id'] = self.env.user.id
                if not vals_copy.get('employee_id'):
                    submitter_id = vals_copy.get('user_id') or self.env.user.id
                    submitter = self.env['res.users'].sudo().browse(submitter_id)
                    vals_copy['employee_id'] = self.env['hr.expense']._ensure_employee_for_user(submitter).id
                    vals_copy.setdefault('user_id', submitter_id)
            cleaned_vals_list.append(vals_copy)

        records = super().create(cleaned_vals_list)
        if not allow_snapshot:
            for record in records.filtered('project_id'):
                submitter = record.user_id or record.employee_id.user_id
                rate = submitter._get_effective_hourly_cost() if submitter else (record.employee_id.sudo().hourly_cost or 0.0)
                record.sudo().with_context(_projectops_allow_snapshot_write=True).write({
                    'hourly_rate_snapshot': rate,
                })
        return records

    def write(self, vals):
        if not self.env.su:
            self.check_access('write')
        allow_snapshot = self.env.context.get('_projectops_allow_snapshot_write')
        allow_transition = self.env.context.get('_projectops_workflow_transition')

        project_lines = self.filtered('project_id')
        if project_lines:
            if not allow_snapshot and 'hourly_rate_snapshot' in vals:
                raise UserError("Hourly rate snapshot cannot be modified manually.")
            if 'unit_amount' in vals and (vals['unit_amount'] is False or vals['unit_amount'] <= 0.0):
                raise ValidationError("Worklog hours must be strictly positive.")
            if 'name' in vals and (not vals['name'] or not str(vals['name']).strip()):
                raise ValidationError("Worklog description cannot be empty.")
            if not allow_transition:
                if 'status' in vals:
                    raise UserError("Worklog status must be changed through workflow actions.")
                for record in project_lines:
                    if record.status != 'draft':
                        raise UserError("Only draft worklogs can be modified.")

        res = super().write(vals)
        if not allow_snapshot and ('user_id' in vals or 'employee_id' in vals):
            for record in project_lines:
                if record.status == 'draft':
                    submitter = record.user_id or record.employee_id.user_id
                    rate = submitter._get_effective_hourly_cost() if submitter else (record.employee_id.sudo().hourly_cost or 0.0)
                    record.sudo().with_context(_projectops_allow_snapshot_write=True).write({
                        'hourly_rate_snapshot': rate,
                    })
        return res

    @api.ondelete(at_uninstall=False)
    def _unlink_only_draft_worklogs(self):
        if not self.env.su:
            self.check_access('unlink')
        for record in self.filtered('project_id'):
            if record.status != 'draft':
                raise UserError("Only draft worklogs can be deleted.")

    def action_submit(self):
        self.check_access('write')
        is_manager = self.env.user.has_group('projectops_core.group_projectops_project_manager')
        for worklog in self:
            if not worklog.project_id:
                raise ValidationError("A project is required to submit a worklog.")
            if worklog.status != 'draft':
                raise UserError("Only draft worklogs can be submitted.")
            submitter = worklog.user_id or worklog.employee_id.user_id
            if not is_manager and submitter != self.env.user:
                raise AccessError("You can only submit your own worklogs.")
            if worklog.unit_amount <= 0.0:
                raise ValidationError("Worklog hours must be strictly positive.")
            if not worklog.name or not worklog.name.strip():
                raise ValidationError("Worklog description cannot be empty.")
            if worklog.task_id and worklog.task_id.project_id != worklog.project_id:
                raise ValidationError("The selected task must belong to the same project as the worklog.")
            if submitter:
                worklog._validate_submitter_on_project(submitter, worklog.project_id)

            rate = submitter._get_effective_hourly_cost() if submitter else (worklog.employee_id.sudo().hourly_cost or 0.0)
            worklog.sudo().with_context(
                _projectops_workflow_transition=True,
                _projectops_allow_snapshot_write=True,
            ).write({
                'status': 'submitted',
                'hourly_rate_snapshot': rate,
            })
