# School Finance methods are defined in here
from odoo import api, fields, models


class SchoolFees(models.Model):
    _name = 'school.fees'
    _description = 'School Fees'

    name = fields.Char(string='Fee Name', required=True)
    category_id = fields.Many2one('school.fees.category', string='Category', required=True,
                                  default=lambda self: self.env['school.fees.category'].search([('name', '=', 'Tuition Fees')], limit=1).id)
    amount = fields.Float(string='Amount', required=True)
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='Due Date')
    student_ids = fields.Many2many('student.info', string='Students')
    month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
                              ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'), ('9', 'September'),
                              ('10', 'October'), ('11', 'November'), ('12', 'December')],string='Month', required=True)


    @api.onchange('category_id')
    def onchange_category_id(self):
        if self.category_id:
            self.amount = self.category_id.amount


    # payment_term_id = fields.Many2one('account.payment.term', string='Payment Term', required=True)
    # payment_method_id = fields.Many2one('account.payment.method', string='Payment Method', required=True)

class SchoolFeesCategory(models.Model):
    _name = 'school.fees.category'
    _description = 'School Fees Category'

    name = fields.Char(string='Category Name', required=True)
    amount = fields.Float(string="Amount")
    description = fields.Text(string="Description")
    course_ids = fields.Many2many('school.course', string='Courses')


class SchoolPayroll(models.Model):
    _name = 'school.payroll'
    _description = 'School Payroll'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    job_id = fields.Many2one('hr.job', string='Job Position', required=True)
    basic_pay = fields.Float(string='Basic Pay', required=True)
    allowances = fields.Float(string='Allowances')
    deductions = fields.Float(string='Deductions')
    net_pay = fields.Float(string='Net Pay', compute='_compute_net_pay', store=True)
    pay_date = fields.Date(string='Pay Date', required=True)

    @api.depends('basic_pay', 'allowances', 'deductions')
    def _compute_net_pay(self):
        for rec in self:
            rec.net_pay = rec.basic_pay + rec.allowances - rec.deductions


class SchoolJobPosition(models.Model):
    _name = 'school.job.position'
    _description = 'School Job Position'

    name = fields.Char(string='Position Name', required=True)
    salary_category_ids = fields.Many2many('school.salary.category', string='Salary Categories')


class SchoolSalaryCategory(models.Model):
    _name = 'school.salary.category'
    _description = 'School Salary Category'

    name = fields.Char(string='Category Name', required=True)



