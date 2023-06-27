from odoo import api, fields, models, _
from datetime import datetime
from datetime import date
from dateutil import relativedelta
from odoo.exceptions import ValidationError, UserError


class SchoolApplicationRegister(models.Model):
    _name = 'school.applicationregister'
    _description = 'School Application Register'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def check_current_year(self):
        '''Method to get default value of logged in Student'''
        res = self.env['schoolacademic.year'].search([('current', '=', True)])
        if not res:
            raise ValidationError(_(
                "There is no current Academic Year defined! Please contact Administator!"))
        return res.id


    # @api.model
    # def default_application_number(self):
    #     return self.env['ir.sequence'].next_by_code('school.applicationregister')

    name = fields.Char('Name', required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender")
    date_of_birth = fields.Date(string="Date of Birth")
    age = fields.Integer(string="Age", compute="_compute_age", inverse="_inverse_compute_age",
                         search="_search_age", tracking=True)
    # look, this commented section is for the school field inheriting from school.info, it caused error so I have removed
    # school = fields.Many2one('school.info', string="School", default=lambda self: self._default_school())
    school = fields.Char(string="School", default="Quule Adan Secondary School")
    image = fields.Image(string="Image")
    standard = fields.Many2one('school.standards', string="Standard")
    school_class = fields.Many2one('school.division', string="Class", domain="[('standard_id', '=', standard)]")
    student_id = fields.Char(string="Student ID")
    academic_year = fields.Many2one('schoolacademic.year', string="Academic Year", default=check_current_year,
                                    help='Select academic year', tracking=True)
    address_one = fields.Char(string="Address")
    district = fields.Selection([('ahmed_dhagah', 'Ahmed-Dhagah'), ('thirtyfirst_may', '31 May'),
                                 ('mohamoud_haybe', 'Mohamoud Haybe'), ('twentysix_june', '26 June'),
                                 ('gacan_libah', 'Gacan Libaah'), ('mohamed_moge', 'Mohamed Moge'),
                                 ('ibrahin_kodbur', 'Ibrahin Kodbur'), ('macalin_harun', 'Macalin Harun')],
                                string="District")
    city = fields.Char(default="Hargeisa")
    class_division = fields.Char(string="Class Division", readonly=True, compute='_compute_class_division')
    # admission_number = fields.Char(string="Admission Number", default=lambda self: self._context.get('default_admission_number',
    #                                                                  self.env['ir.sequence'].next_by_code('school.applicationregister')))
    application_number = fields.Char('Application Number', default="New")
    is_saved = fields.Boolean('Is Saved', default=False)
    admission_date = fields.Date(
        'Admission Date', copy=False)
        # states={'done': [('readonly', True)]})
    application_date = fields.Datetime(
        'Application Date', required=True, copy=False,
        state={'done': [('readonly', True)]},
        default=lambda self: fields.Datetime.now())
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submitted'), ('confirm', 'Confirmed'),
                              ('cancel', 'Cancelled'), ('done', 'Done')], 'Status', default='draft', tracking=True)
    reference_ids = fields.One2many('student.parent', 'parent_id', 'References')
    previous_school_ids = fields.One2many('previous.school', 'previous_school_id', string="Previous School IDs")
    paid = fields.Boolean(string="Paid", default=False)
    fees = fields.Char(string="Fees", default=10000)
    fee_start = fields.Date(string="Fee Start Date")
    ribbon_visible = fields.Boolean(compute='_compute_ribbon_visible', store=True)
    active = fields.Boolean(default=True)

    # look, this commented section is for the school field inheriting from school.info, it caused error so I have removed
    # def _default_school(self):
    #     default_school = self.env['school.info'].browse(1)  # Fetch the school with ID 1
    #     return default_school if default_school else False

    # I have commented this, because other write def is being defined, and moved the code in to that
    # def write(self, vals):
    #     if vals.get('state') == 'done' and not self.paid:
    #         raise ValidationError("Cannot move to Done state until the fee is paid.")
    #     return super(SchoolApplicationRegister, self).write(vals)

    @api.depends('standard', 'school_class')
    def _compute_class_division(self):
        for rec in self:
            rec.class_division = f"{rec.standard.name} - {rec.school_class.name}"

    @api.depends('state', 'paid')
    def _compute_ribbon_visible(self):
        for record in self:
            if record.state == 'done' and record.paid:
                record.ribbon_visible = True
            else:
                record.ribbon_visible = False

    def example_button(self):
        # Add your custom code here
        self.write({'state': 'confirm'})

    def submit_form(self):
        self.state = 'submit'

    def confirm_in_progress(self):
        for record in self:
            record.state = 'confirm'
            # paid = record.paid
            # if paid == True:
            #     record.state = 'confirm'
            # else:
            #     raise ValidationError("First Pay The Fee")


    def confirm_to_draft(self):
        self.state = 'draft'

    def confirm_cancel(self):
        self.state = 'cancel'
        # if self.is_student and self.student_id.fees_detail_ids:
        #     self.student_id.fees_detail_ids.state = 'cancel'

    # @api.multi
    def enroll_student(self):
        # look, this commented section is for the school field inheriting from school.info, it caused error so I have removed
        # default_school = self._default_school()
        # if not default_school:
        #     raise ValidationError("No default school found.")

        # Check if student already enrolled
        existing_student = self.env['student.info'].search([('application_number', '=', self.application_number)])
        if existing_student:
            raise ValidationError("This student has already been enrolled.")
        # Create new student record
        new_student = self.env['student.info'].create({
            'name': self.name,
            'gender': self.gender,
            'date_of_birth': self.date_of_birth,
            'age': self.age,
            'school': self.school,
            'image': self.image,
            'standard': self.standard.id,
            'school_class': self.school_class.id,
            'academic_year': self.academic_year.id,
            'class_division': self.class_division,
            'address_one': self.address_one,
            'district': self.district,
            'city': self.city,
            'reference_ids': [(0, 0, {
                'parent_name': ref.parent_name,
                'phone': ref.phone,
                'relation': ref.relation,
            }) for ref in self.reference_ids],
            'previous_school_ids': [(0, 0, {
                'name': school.name,
                'standard': school.standard.id,
                'grade': school.grade,
            }) for school in self.previous_school_ids],
        })
        if self.paid:
             self.state = 'done'
        else:
             raise ValidationError("First Pay The Fee")



    @api.model
    def create(self, vals):
        vals['is_saved'] = False
        return super(SchoolApplicationRegister, self).create(vals)

    def write(self, vals):
        if vals.get('state') == 'done' and not self.paid:
            raise ValidationError("Cannot move to Done state until the fee is paid.")

        if not self.is_saved and self.id:
            vals['application_number'] = self.env['ir.sequence'].next_by_code('school.applicationregister')
            vals['is_saved'] = True
        return super(SchoolApplicationRegister, self).write(vals)


    @api.depends('date_of_birth')
    def _compute_age(self):
        today = date.today()
        for rec in self:
            if rec.date_of_birth:
                rec.age = today.year - rec.date_of_birth.year
            else:
                rec.age = 1

    @api.depends('age')
    def _inverse_compute_age(self):
        today = date.today()
        for rec in self:
            rec.date_of_birth = today - relativedelta.relativedelta(years=rec.age)
