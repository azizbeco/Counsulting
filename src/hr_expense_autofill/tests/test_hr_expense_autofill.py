from odoo.tests import Form, tagged

from odoo.addons.hr_expense.tests.common import TestExpenseCommon


@tagged('-at_install', 'post_install')
class TestHrExpenseAutofill(TestExpenseCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.sudo().group_ids += cls.env.ref('analytic.group_analytic_accounting')
        cls.customer = cls.env['res.partner'].create({'name': 'Customer'})
        cls.plan = cls.env['account.analytic.plan'].sudo().create({'name': 'Projects'})
        cls.analytic = cls.env['account.analytic.account'].sudo().create({
            'name': 'Customer Project',
            'plan_id': cls.plan.id,
        })
        cls.other_analytic = cls.env['account.analytic.account'].sudo().create({
            'name': 'Other',
            'plan_id': cls.plan.id,
        })
        cls.project = cls.env['project.project'].sudo().create({
            'name': 'Customer Project',
            'partner_id': cls.customer.id,
            'account_id': cls.analytic.id,
        })

    def test_defaults(self):
        with Form(self.env['hr.expense']) as expense_form:
            expense_form.name = 'Taxi'
            self.assertFalse(expense_form.product_id)
            self.assertEqual(expense_form.payment_mode, 'company_account')
            expense_form.product_id = self.product_a
            expense_form.employee_id = self.expense_employee

    def test_vendor_sets_project_analytic(self):
        with Form(self.env['hr.expense']) as expense_form:
            expense_form.name = 'Taxi'
            expense_form.product_id = self.product_a
            expense_form.employee_id = self.expense_employee
            expense_form.analytic_distribution = {str(self.other_analytic.id): 100}
            expense_form.vendor_id = self.customer
            self.assertEqual(expense_form.analytic_distribution, {str(self.analytic.id): 100})
