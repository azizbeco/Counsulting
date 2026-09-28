from odoo import api, fields, models


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    payment_mode = fields.Selection(default='company_account')

    def _onchange_predict_product(self):
        # Category must be chosen by the user, never predicted from the description.
        return

    @api.depends('vendor_id')
    def _compute_analytic_distribution(self):
        super()._compute_analytic_distribution()
        # Opened from a project: keep that project's distribution (project_hr_expense).
        if self.env.context.get('project_id'):
            return
        Project = self.env['project.project'].sudo()
        for expense in self.filtered('vendor_id'):
            project = Project.search([
                ('partner_id', 'child_of', expense.vendor_id.commercial_partner_id.id),
                ('account_id', '!=', False),
                ('company_id', 'in', [expense.company_id.id, False]),
            ], limit=1)
            distribution = project._get_analytic_distribution()
            if distribution:
                expense.analytic_distribution = distribution
