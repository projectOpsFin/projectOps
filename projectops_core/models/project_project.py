# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_code = fields.Char(
        string='Project Code',
        required=True,
        copy=False,
        index=True,
        tracking=True,
        help='Unique identifier for the project.',
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        tracking=True,
        domain="['|', ('company_id', '=?', company_id), ('company_id', '=', False)]",
        help='Associated customer for this project.',
    )
    owner_user_id = fields.Many2one(
        'res.users',
        string='Project Owner',
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
        help='Designated owner responsible for project oversight.',
    )
    start_date = fields.Date(
        string='Start Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
        help='Project start date.',
    )
    end_date = fields.Date(
        string='Planned End Date',
        tracking=True,
        help='Planned completion date for the project.',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Project Currency',
        compute='_compute_currency_id',
        store=True,
        readonly=False,
        default=lambda self: self.env.company.currency_id,
        help='Currency used for all project monetary calculations.',
    )
    contract_value = fields.Monetary(
        string='Contract Value',
        currency_field='currency_id',
        required=True,
        default=0.0,
        tracking=True,
        groups='projectops_core.group_projectops_project_manager,projectops_core.group_projectops_finance',
        help='Agreed total contract value for the project.',
    )
    cost_budget = fields.Monetary(
        string='Cost Budget',
        currency_field='currency_id',
        required=True,
        default=0.0,
        tracking=True,
        groups='projectops_core.group_projectops_project_manager,projectops_core.group_projectops_finance',
        help='Approved cost budget for labor and expenses.',
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
        ],
        string='Project Status',
        default='draft',
        required=True,
        copy=False,
        tracking=True,
        index=True,
        help='Current lifecycle status of the project.',
    )
    assignment_ids = fields.One2many(
        'projectops.assignment',
        'project_id',
        string='Team Assignments',
        help='Team members assigned to this project and their designated roles.',
    )
    assigned_user_ids = fields.Many2many(
        'res.users',
        string='Assigned Team Members',
        compute='_compute_assigned_user_ids',
        store=True,
        help='All active users currently assigned to this project.',
    )

    privacy_visibility = fields.Selection(
        default='followers',
    )

    _unique_project_code = models.Constraint(
        'UNIQUE(project_code)',
        'The project code must be unique.',
    )
    _check_project_dates = models.Constraint(
        'CHECK(end_date IS NULL OR start_date IS NULL OR end_date >= start_date)',
        'The planned end date cannot be earlier than the start date.',
    )
    _check_contract_value = models.Constraint(
        'CHECK(contract_value >= 0)',
        'Contract value must be non-negative.',
    )
    _check_cost_budget = models.Constraint(
        'CHECK(cost_budget >= 0)',
        'Cost budget must be non-negative.',
    )

    def _validate_project_vals(self, vals, is_create=True):
        if is_create and not vals.get('customer_id') and not vals.get('partner_id'):
            raise ValidationError("Every project must have a customer.")
        if is_create and not vals.get('owner_user_id') and not vals.get('user_id'):
            raise ValidationError("Every project must have a designated owner.")
        if 'project_code' in vals:
            code = vals.get('project_code')
            if not code or not str(code).strip():
                raise ValidationError("Project code cannot be empty.")
            duplicate = self.search([
                ('project_code', '=', str(code).strip()),
                ('id', 'not in', self.ids),
            ])
            if duplicate:
                raise ValidationError(f"Project code '{code}' already exists. Project codes must be unique.")
        start_date = vals.get('start_date') or (self.start_date if not is_create else None)
        end_date = vals.get('end_date') or (self.end_date if not is_create else None)
        if start_date and end_date and str(end_date) < str(start_date):
            raise ValidationError("The planned end date cannot be earlier than the start date.")
        if 'contract_value' in vals and vals.get('contract_value', 0.0) < 0.0:
            raise ValidationError("Contract value must be non-negative.")
        if 'cost_budget' in vals and vals.get('cost_budget', 0.0) < 0.0:
            raise ValidationError("Cost budget must be non-negative.")

    @api.depends('company_id')
    def _compute_currency_id(self):
        default_currency = self.env.company.currency_id
        for project in self:
            if not project.currency_id:
                project.currency_id = project.company_id.currency_id or default_currency

    @api.depends('assignment_ids.user_id', 'assignment_ids.active')
    def _compute_assigned_user_ids(self):
        for project in self:
            active_assignments = project.assignment_ids.filtered('active')
            project.assigned_user_ids = active_assignments.mapped('user_id')

    # Synchronize ProjectOps fields with native Odoo project.project fields
    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        if self.customer_id:
            self.partner_id = self.customer_id

    @api.onchange('owner_user_id')
    def _onchange_owner_user_id(self):
        if self.owner_user_id:
            self.user_id = self.owner_user_id

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date:
            self.date_start = self.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.end_date:
            self.date = self.end_date

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._validate_project_vals(vals, is_create=True)
            if 'customer_id' in vals and 'partner_id' not in vals:
                vals['partner_id'] = vals['customer_id']
            elif 'partner_id' in vals and 'customer_id' not in vals:
                vals['customer_id'] = vals['partner_id']

            if 'owner_user_id' in vals and 'user_id' not in vals:
                vals['user_id'] = vals['owner_user_id']
            elif 'user_id' in vals and 'owner_user_id' not in vals:
                vals['owner_user_id'] = vals['user_id']

            if 'start_date' in vals and 'date_start' not in vals:
                vals['date_start'] = vals['start_date']
            elif 'date_start' in vals and 'start_date' not in vals:
                vals['start_date'] = vals['date_start']

            if 'end_date' in vals and 'date' not in vals:
                vals['date'] = vals['end_date']
            elif 'date' in vals and 'end_date' not in vals:
                vals['end_date'] = vals['date']

        return super().create(vals_list)

    def write(self, vals):
        self._validate_project_vals(vals, is_create=False)
        if 'customer_id' in vals and 'partner_id' not in vals:
            vals['partner_id'] = vals['customer_id']
        elif 'partner_id' in vals and 'customer_id' not in vals:
            vals['customer_id'] = vals['partner_id']

        if 'owner_user_id' in vals and 'user_id' not in vals:
            vals['user_id'] = vals['owner_user_id']
        elif 'user_id' in vals and 'owner_user_id' not in vals:
            vals['owner_user_id'] = vals['user_id']

        if 'start_date' in vals and 'date_start' not in vals:
            vals['date_start'] = vals['start_date']
        elif 'date_start' in vals and 'start_date' not in vals:
            vals['start_date'] = vals['date_start']

        if 'end_date' in vals and 'date' not in vals:
            vals['date'] = vals['end_date']
        elif 'date' in vals and 'end_date' not in vals:
            vals['end_date'] = vals['date']

        return super().write(vals)

    @api.constrains('project_code')
    def _check_project_code_unique(self):
        for project in self:
            if not project.project_code or not project.project_code.strip():
                raise ValidationError("Project code cannot be empty.")
            duplicate = self.search([
                ('project_code', '=', project.project_code.strip()),
                ('id', '!=', project.id),
            ])
            if duplicate:
                raise ValidationError(f"Project code '{project.project_code}' already exists. Project codes must be unique.")

    @api.constrains('start_date', 'end_date')
    def _check_dates_consistency(self):
        for project in self:
            if project.start_date and project.end_date and project.end_date < project.start_date:
                raise ValidationError("The planned end date cannot be earlier than the start date.")

    @api.constrains('contract_value', 'cost_budget')
    def _check_financial_values(self):
        for project in self:
            if project.contract_value < 0.0:
                raise ValidationError("Contract value must be non-negative.")
            if project.cost_budget < 0.0:
                raise ValidationError("Cost budget must be non-negative.")

    @api.constrains('customer_id')
    def _check_customer_required(self):
        for project in self:
            if not project.customer_id:
                raise ValidationError("Every project must have a customer.")

    @api.constrains('owner_user_id')
    def _check_owner_required(self):
        for project in self:
            if not project.owner_user_id:
                raise ValidationError("Every project must have a designated owner.")

    # Lifecycle workflow methods
    def action_activate(self):
        for project in self:
            if project.state != 'draft':
                raise UserError("Only draft projects can be activated.")
            if not project.customer_id:
                raise UserError("A customer must be assigned before activating the project.")
            if not project.owner_user_id:
                raise UserError("An owner must be designated before activating the project.")
            project.state = 'in_progress'

    def action_complete(self):
        for project in self:
            if project.state != 'in_progress':
                raise UserError("Only in-progress projects can be marked as completed.")
            project.state = 'completed'

    def action_reset_draft(self):
        for project in self:
            if project.state == 'completed' and not self.env.user.has_group('projectops_core.group_projectops_manager'):
                raise UserError("Only an Operations Manager can reopen a completed project.")
            project.state = 'draft'
