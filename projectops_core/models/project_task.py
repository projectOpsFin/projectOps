# -*- coding: utf-8 -*-

from datetime import datetime, time

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError


TASK_STATUS_TO_STATE = {
    'todo': '01_in_progress',
    'in_progress': '01_in_progress',
    'done': '1_done',
    'cancelled': '1_canceled',
}

STATE_TO_TASK_STATUS = {
    '01_in_progress': 'in_progress',
    '02_changes_requested': 'in_progress',
    '03_approved': 'in_progress',
    '04_waiting_normal': 'todo',
    '1_done': 'done',
    '1_canceled': 'cancelled',
}

MANAGER_ONLY_TASK_FIELDS = {
    'project_id',
    'projectops_milestone_id',
    'milestone_id',
    'assignee_user_id',
    'user_ids',
    'title',
    'name',
    'deadline',
    'date_deadline',
}


class ProjectTask(models.Model):
    _inherit = 'project.task'

    projectops_milestone_id = fields.Many2one(
        'projectops.milestone',
        string='ProjectOps Milestone',
        index=True,
        ondelete='set null',
        tracking=True,
        domain="[('project_id', '=', project_id)]",
        help='Optional milestone within the same project.',
    )
    assignee_user_id = fields.Many2one(
        'res.users',
        string='Assignee',
        index=True,
        tracking=True,
        domain="[('share', '=', False), ('active', '=', True)]",
        help='Primary team member assigned to this task.',
    )
    title = fields.Char(
        string='Task Title',
        related='name',
        readonly=False,
        store=True,
        help='Title of the task.',
    )
    deadline = fields.Date(
        string='Task Deadline',
        index=True,
        tracking=True,
        copy=False,
        help='Target completion date for this task.',
    )
    status = fields.Selection(
        selection=[
            ('todo', 'To Do'),
            ('in_progress', 'In Progress'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        string='Task Status',
        required=True,
        default='todo',
        copy=False,
        tracking=True,
        index=True,
        help='Current ProjectOps workflow status of the task.',
    )
    progress = fields.Float(
        string='Progress (%)',
        required=True,
        default=0.0,
        tracking=True,
        help='Task completion percentage between 0 and 100.',
    )
    is_overdue = fields.Boolean(
        string='Is Overdue',
        compute='_compute_is_overdue',
        search='_search_is_overdue',
        help='True when the task deadline has passed and the task is not completed or cancelled.',
    )

    _check_progress_range = models.Constraint(
        'CHECK(progress >= 0 AND progress <= 100)',
        'Task progress must be between 0 and 100.',
    )

    @api.depends('deadline', 'date_deadline', 'status', 'is_closed')
    def _compute_is_overdue(self):
        today = fields.Date.context_today(self)
        for task in self:
            effective_deadline = task.deadline or (task.date_deadline.date() if task.date_deadline else False)
            task.is_overdue = bool(
                effective_deadline
                and effective_deadline < today
                and task.status not in ('done', 'cancelled')
                and not task.is_closed
            )

    def _search_is_overdue(self, operator, value):
        if operator not in ('=', '!=') or not isinstance(value, bool):
            raise UserError("Unsupported search operator for is_overdue.")
        today = fields.Date.context_today(self)
        want_overdue = (operator == '=' and value) or (operator == '!=' and not value)
        overdue_domain = [
            ('status', 'not in', ['done', 'cancelled']),
            ('is_closed', '=', False),
            '|',
            ('deadline', '<', today),
            '&',
            ('deadline', '=', False),
            ('date_deadline', '<', datetime.combine(today, time.min)),
        ]
        if want_overdue:
            return overdue_domain
        return ['!'] + overdue_domain

    @api.constrains('project_id')
    def _check_project_required(self):
        if self.env.su:
            return
        for task in self:
            if not task.project_id:
                raise ValidationError("Every task must belong to a valid project.")

    @api.constrains('assignee_user_id')
    def _check_assignee_required(self):
        if self.env.su:
            return
        for task in self:
            if not task.assignee_user_id:
                raise ValidationError("Every task must have an assigned user.")

    @api.constrains('project_id', 'projectops_milestone_id')
    def _check_milestone_same_project(self):
        for task in self:
            if task.projectops_milestone_id and task.projectops_milestone_id.project_id != task.project_id:
                raise ValidationError("A task's milestone must belong to the same project as the task.")

    @api.constrains('progress')
    def _check_progress_bounds(self):
        for task in self:
            if task.progress < 0.0 or task.progress > 100.0:
                raise ValidationError("Task progress must be between 0 and 100.")

    @api.model
    def _sync_task_vals(self, vals):
        """Keep ProjectOps task fields synchronized with native project.task fields."""
        synced = dict(vals)

        if 'title' in synced and 'name' not in synced:
            synced['name'] = synced.pop('title')
        elif 'title' in synced and 'name' in synced:
            synced.pop('title')

        if 'assignee_user_id' in synced and 'user_ids' not in synced:
            uid = synced['assignee_user_id']
            synced['user_ids'] = [(6, 0, [uid])] if uid else [(5, 0, 0)]
        elif 'user_ids' in synced and 'assignee_user_id' not in synced:
            # Extract first user if Command.set or list of ids is given
            commands = synced['user_ids'] or []
            if len(commands) == 1 and isinstance(commands[0], (list, tuple)) and commands[0][0] == 6:
                uids = commands[0][2]
                synced['assignee_user_id'] = uids[0] if uids else False

        if 'deadline' in synced and 'date_deadline' not in synced:
            deadline_val = synced['deadline']
            if deadline_val:
                d = fields.Date.to_date(deadline_val)
                synced['date_deadline'] = datetime.combine(d, time(23, 59, 59))
            else:
                synced['date_deadline'] = False
        elif 'date_deadline' in synced and 'deadline' not in synced:
            dt_val = synced['date_deadline']
            synced['deadline'] = fields.Datetime.to_datetime(dt_val).date() if dt_val else False

        if 'status' in synced and 'state' not in synced:
            synced['state'] = TASK_STATUS_TO_STATE.get(synced['status'], '01_in_progress')
        elif 'state' in synced and 'status' not in synced:
            synced['status'] = STATE_TO_TASK_STATUS.get(synced['state'], 'in_progress')

        if synced.get('status') == 'done' and 'progress' not in synced:
            synced['progress'] = 100.0

        return synced

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su and not self.env.user.has_group('projectops_core.group_projectops_project_manager'):
            raise AccessError("Only Project Managers or Operations Managers can create tasks.")
        synced_list = [self._sync_task_vals(vals) for vals in vals_list]
        if not self.env.su:
            for vals in synced_list:
                if not vals.get('project_id'):
                    raise ValidationError("Every task must belong to a valid project.")
                if not vals.get('assignee_user_id'):
                    raise ValidationError("Every task must have an assigned user.")
        return super().create(synced_list)

    def write(self, vals):
        if not self.env.su and not self.env.user.has_group('projectops_core.group_projectops_project_manager'):
            restricted = MANAGER_ONLY_TASK_FIELDS.intersection(vals.keys())
            if restricted:
                raise AccessError(
                    "Team Members cannot modify task project, milestone, assignee, title, or deadline."
                )
        synced = self._sync_task_vals(vals)
        return super().write(synced)

    def _check_task_action_permission(self, manager_only=False):
        is_manager = self.env.user.has_group('projectops_core.group_projectops_project_manager')
        if is_manager:
            return
        if manager_only:
            raise AccessError("Only Project Managers or Operations Managers can perform this task action.")
        for task in self:
            if task.assignee_user_id != self.env.user and self.env.user not in task.user_ids:
                raise AccessError("You can only update tasks assigned to you.")

    def action_start(self):
        self._check_task_action_permission(manager_only=False)
        for task in self:
            if task.status in ('done', 'cancelled'):
                raise UserError("Completed or cancelled tasks must be reopened before starting.")
            task.write({'status': 'in_progress'})

    def action_mark_done(self):
        self._check_task_action_permission(manager_only=False)
        for task in self:
            if task.status == 'cancelled':
                raise UserError("Cancelled tasks cannot be marked as done.")
            task.write({'status': 'done', 'progress': 100.0})

    def action_cancel(self):
        self._check_task_action_permission(manager_only=True)
        for task in self:
            if task.status == 'done':
                raise UserError("Completed tasks cannot be cancelled.")
            task.write({'status': 'cancelled'})

    def action_reopen(self):
        self._check_task_action_permission(manager_only=True)
        for task in self:
            if task.status not in ('done', 'cancelled'):
                raise UserError("Only completed or cancelled tasks can be reopened.")
            task.write({'status': 'in_progress'})
