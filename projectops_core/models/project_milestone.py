# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError


class ProjectopsMilestone(models.Model):
    _name = 'projectops.milestone'
    _description = 'ProjectOps Milestone'
    _order = 'sequence, due_date, id'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        ondelete='cascade',
        index=True,
        help='Project to which this milestone belongs.',
    )
    title = fields.Char(
        string='Title',
        required=True,
        help='Milestone title.',
    )
    description = fields.Text(
        string='Description',
        help='Detailed description of milestone deliverables.',
    )
    due_date = fields.Date(
        string='Due Date',
        index=True,
        help='Target completion date for this milestone.',
    )
    status = fields.Selection(
        selection=[
            ('planned', 'Planned'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        required=True,
        default='planned',
        copy=False,
        index=True,
        help='Current status of the milestone.',
    )
    sequence = fields.Integer(
        string='Sequence',
        required=True,
        default=10,
        help='Display order of the milestone within the project.',
    )
    task_ids = fields.One2many(
        'project.task',
        'projectops_milestone_id',
        string='Tasks',
        help='Tasks linked to this milestone.',
    )
    task_count = fields.Integer(
        string='Task Count',
        compute='_compute_task_count',
    )

    _check_sequence_non_negative = models.Constraint(
        'CHECK(sequence >= 0)',
        'Milestone sequence must be zero or positive.',
    )

    @api.depends('task_ids')
    def _compute_task_count(self):
        for milestone in self:
            milestone.task_count = len(milestone.task_ids)

    @api.constrains('project_id')
    def _check_project_required(self):
        for milestone in self:
            if not milestone.project_id:
                raise ValidationError("Every milestone must belong to a valid project.")

    @api.constrains('title')
    def _check_title_not_empty(self):
        for milestone in self:
            if not milestone.title or not milestone.title.strip():
                raise ValidationError("Milestone title cannot be empty.")

    @api.constrains('sequence')
    def _check_sequence_valid(self):
        for milestone in self:
            if milestone.sequence < 0:
                raise ValidationError("Milestone sequence must be zero or positive.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('project_id'):
                raise ValidationError("Every milestone must belong to a valid project.")
            if vals.get('sequence', 10) < 0:
                raise ValidationError("Milestone sequence must be zero or positive.")
        return super().create(vals_list)

    def write(self, vals):
        if 'project_id' in vals and not vals.get('project_id'):
            raise ValidationError("Every milestone must belong to a valid project.")
        if 'sequence' in vals and vals.get('sequence', 0) < 0:
            raise ValidationError("Milestone sequence must be zero or positive.")
        return super().write(vals)

    def _check_manager_permission(self):
        if not self.env.user.has_group('projectops_core.group_projectops_project_manager'):
            raise AccessError("Only Project Managers or Operations Managers can change milestone status.")

    def action_start(self):
        self._check_manager_permission()
        for milestone in self:
            if milestone.status != 'planned':
                raise UserError("Only planned milestones can be started.")
            milestone.status = 'in_progress'

    def action_complete(self):
        self._check_manager_permission()
        for milestone in self:
            if milestone.status not in ('planned', 'in_progress'):
                raise UserError("Only planned or in-progress milestones can be marked as completed.")
            milestone.status = 'completed'

    def action_cancel(self):
        self._check_manager_permission()
        for milestone in self:
            if milestone.status == 'completed':
                raise UserError("Completed milestones cannot be cancelled.")
            milestone.status = 'cancelled'

    def action_reopen(self):
        self._check_manager_permission()
        for milestone in self:
            if milestone.status not in ('completed', 'cancelled'):
                raise UserError("Only completed or cancelled milestones can be reopened.")
            milestone.status = 'planned'
