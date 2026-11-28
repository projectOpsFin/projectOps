# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProjectopsAssignment(models.Model):
    _name = 'projectops.assignment'
    _description = 'ProjectOps Team Assignment'
    _inherit = ['mail.thread']
    _order = 'project_id, user_id'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Assigned User',
        required=True,
        index=True,
        tracking=True,
    )
    project_role = fields.Selection(
        selection=[
            ('manager', 'Project Manager'),
            ('lead', 'Technical Lead'),
            ('member', 'Team Member'),
            ('consultant', 'Consultant'),
            ('qa', 'QA Specialist'),
        ],
        string='Project Role',
        required=True,
        default='member',
        tracking=True,
    )
    start_date = fields.Date(
        string='Assignment Start',
        tracking=True,
    )
    end_date = fields.Date(
        string='Assignment End',
        tracking=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True,
    )

    _unique_project_user = models.Constraint(
        'UNIQUE(project_id, user_id)',
        'A user cannot have duplicate assignment records for the same project.',
    )

    @api.constrains('start_date', 'end_date')
    def _check_assignment_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.end_date < record.start_date:
                raise ValidationError("The assignment end date cannot be earlier than its start date.")

    @api.constrains('project_id', 'user_id')
    def _check_duplicate_assignment(self):
        for record in self:
            duplicates = self.with_context(active_test=False).search([
                ('project_id', '=', record.project_id.id),
                ('user_id', '=', record.user_id.id),
                ('id', '!=', record.id),
            ])
            if duplicates:
                raise ValidationError("A user cannot have duplicate assignment records for the same project.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('project_id') and vals.get('user_id'):
                existing = self.with_context(active_test=False).search([
                    ('project_id', '=', vals['project_id']),
                    ('user_id', '=', vals['user_id']),
                ])
                if existing:
                    raise ValidationError("A user cannot have duplicate assignment records for the same project.")
        records = super().create(vals_list)
        for record in records:
            if record.user_id and record.project_id and record.active:
                record.project_id.message_subscribe(partner_ids=[record.user_id.partner_id.id])
        return records

    def write(self, vals):
        if vals.get('project_id') or vals.get('user_id'):
            for record in self:
                p_id = vals.get('project_id', record.project_id.id)
                u_id = vals.get('user_id', record.user_id.id)
                existing = self.with_context(active_test=False).search([
                    ('project_id', '=', p_id),
                    ('user_id', '=', u_id),
                    ('id', '!=', record.id),
                ])
                if existing:
                    raise ValidationError("A user cannot have duplicate assignment records for the same project.")
        res = super().write(vals)
        if 'active' in vals or 'user_id' in vals or 'project_id' in vals:
            for record in self:
                if not record.project_id or not record.user_id:
                    continue
                if record.active:
                    record.project_id.message_subscribe(partner_ids=[record.user_id.partner_id.id])
                elif record.user_id != record.project_id.owner_user_id:
                    record.project_id.message_unsubscribe(partner_ids=[record.user_id.partner_id.id])
        return res

    def unlink(self):
        to_unsubscribe = [
            (rec.project_id, rec.user_id.partner_id)
            for rec in self
            if rec.project_id and rec.user_id and rec.user_id != rec.project_id.owner_user_id
        ]
        res = super().unlink()
        for project, partner in to_unsubscribe:
            project.message_unsubscribe(partner_ids=[partner.id])
        return res
