# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    billing_address = fields.Text(
        string='Billing Address',
        help='Customer billing address for ProjectOps operations and invoices.',
    )
    is_projectops_customer = fields.Boolean(
        string='Is ProjectOps Customer',
        default=False,
        index=True,
        help='Indicates whether this contact is a registered ProjectOps customer.',
    )
    projectops_project_ids = fields.One2many(
        'project.project',
        'customer_id',
        string='ProjectOps Projects',
    )
    projectops_project_count = fields.Integer(
        string='Projects Count',
        compute='_compute_projectops_project_count',
    )

    @api.depends('projectops_project_ids')
    def _compute_projectops_project_count(self):
        for partner in self:
            partner.projectops_project_count = len(partner.projectops_project_ids)
