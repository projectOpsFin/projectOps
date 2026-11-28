# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    hourly_cost_currency_id = fields.Many2one(
        'res.currency',
        string='Hourly Rate Currency',
        related='company_id.currency_id',
        readonly=True,
    )
    hourly_cost_rate = fields.Monetary(
        string='Hourly Cost Rate',
        currency_field='hourly_cost_currency_id',
        default=0.0,
        groups='projectops_core.group_projectops_project_manager,projectops_core.group_projectops_finance',
        help="User's applicable hourly cost rate synced with hr.employee.hourly_cost when an employee record exists.",
    )

    _check_hourly_cost_rate_non_negative = models.Constraint(
        'CHECK(hourly_cost_rate >= 0)',
        'Hourly cost rate must be non-negative.',
    )

    @api.constrains('hourly_cost_rate')
    def _check_hourly_cost_rate_value(self):
        for user in self:
            if user.hourly_cost_rate < 0.0:
                raise ValidationError("Hourly cost rate must be non-negative.")

    def _get_effective_hourly_cost(self):
        """Return hr.employee.hourly_cost if set, otherwise fallback to res.users.hourly_cost_rate."""
        self.ensure_one()
        user_sudo = self.sudo()
        if user_sudo.employee_id and user_sudo.employee_id.hourly_cost:
            return user_sudo.employee_id.hourly_cost
        return user_sudo.hourly_cost_rate or 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('hourly_cost_rate', 0.0) < 0.0:
                raise ValidationError("Hourly cost rate must be non-negative.")
        records = super().create(vals_list)
        for user in records:
            if user.hourly_cost_rate and user.sudo().employee_id:
                user.sudo().employee_id.hourly_cost = user.hourly_cost_rate
        return records

    def write(self, vals):
        if 'hourly_cost_rate' in vals and vals.get('hourly_cost_rate', 0.0) < 0.0:
            raise ValidationError("Hourly cost rate must be non-negative.")
        res = super().write(vals)
        if 'hourly_cost_rate' in vals and not self.env.context.get('_projectops_syncing_hourly_cost'):
            for user in self:
                if user.sudo().employee_id:
                    user.sudo().employee_id.with_context(_projectops_syncing_hourly_cost=True).hourly_cost = user.hourly_cost_rate
        return res


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.constrains('hourly_cost')
    def _check_hourly_cost_non_negative(self):
        for employee in self:
            if employee.hourly_cost < 0.0:
                raise ValidationError("Hourly cost rate must be non-negative.")

    def write(self, vals):
        if 'hourly_cost' in vals and vals.get('hourly_cost', 0.0) < 0.0:
            raise ValidationError("Hourly cost rate must be non-negative.")
        res = super().write(vals)
        if 'hourly_cost' in vals and not self.env.context.get('_projectops_syncing_hourly_cost'):
            for employee in self:
                if employee.user_id:
                    employee.user_id.sudo().with_context(_projectops_syncing_hourly_cost=True).hourly_cost_rate = employee.hourly_cost
        return res
