from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AdministrationInformation(models.Model):
    _name = 'administration.info'
    _description = 'Administration Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True)
    image = fields.Image(string="Image")
    role = fields.Char(string="Role")
    school = fields.Char(string="School", default="Quule Adan Secondary School")
    is_parent = fields.Boolean(string="Is Parent")
    date_of_appointment = fields.Date(string="Date of Appointment")
    admin_id = fields.Char(string="ID")
    address_one = fields.Char(string="Teacher Address")
    district = fields.Selection([('ahmed_dhagah', 'Ahmed-Dhagah'), ('thirtyfirst_may', '31 May'),
                                 ('mohamoud_haybe', 'Mohamoud Haybe'), ('twentysix_june', '26 June'),
                                 ('gacan_libah', 'Gacan Libaah'), ('mohamed_moge', 'Mohamed Moge'),
                                 ('ibrahin_kodbur', 'Ibrahin Kodbur'), ('macalin_harun', 'Macalin Harun')],
                                string="District")
    city = fields.Char(default="Hargeisa")
    working_address = fields.Char(string='Work Address', default="Quule Adan")
    work_village = fields.Char(string="Work District", default="Ahmed-Gurey")
    work_district = fields.Char(string="Work District", default="Ahmed-Dhagah")
    department = fields.Selection([('administration', 'Administration'), ('teacher', 'Teachers'),
                                   ('other_staff', 'Other Staff')], string="Department", default='Administration')
    position = fields.Char(string="Position")
    status = fields.Boolean(string="Principal Status")

    admin_address = fields.Char(string="Teacher Address")
    admin_contact = fields.Char(string="Teacher's Contact")
    admin_email = fields.Char(string="Email")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender")
    marital_status = fields.Selection([('single', 'Single'), ('married', 'Married')])
    date_of_birth = fields.Date(string="Date of Birth")
    color = fields.Selection([('red', 'Red'), ('green', 'Green'), ('blue', 'Blue')], string='Color')

    # this function is used to create the sequence of the student id
    @api.model
    def create(self, vals):
        vals['admin_id'] = self.env['ir.sequence'].next_by_code('administration.info')
        return super(AdministrationInformation, self).create(vals)

    @api.constrains('status')
    def check_status(self):
        '''Constraint on active principal status'''
        status_rec = self.search_count([('status', '=', True)])
        if status_rec >= 2:
            raise ValidationError(_(
                "Error! You cannot set two principals active!"))



class SchoolTeachers(models.Model):
    _name = 'teacher.info'
    _description = 'Teacher Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True)
    image = fields.Image(string="Image")
    subjects = fields.Many2many('school.subject', string="Subjects")
    school = fields.Char(string="School", default="Quule Adan Secondary School")
    is_parent = fields.Boolean(string="Is Parent")
    standards_taught = fields.Many2many('school.standards', string="Standards Taught")

    address_one = fields.Char(string="Teacher Address")
    district = fields.Selection([('ahmed_dhagah', 'Ahmed-Dhagah'), ('thirtyfirst_may', '31 May'),
                                 ('mohamoud_haybe', 'Mohamoud Haybe'), ('twentysix_june', '26 June'),
                                 ('gacan_libah', 'Gacan Libaah'), ('mohamed_moge', 'Mohamed Moge'),
                                 ('ibrahin_kodbur', 'Ibrahin Kodbur'), ('macalin_harun', 'Macalin Harun')],
                                string="District")
    city = fields.Char(default="Hargeisa")
    working_address = fields.Char(string='Work Address', default="Quule Adan")
    work_village = fields.Char(string="Work District", default="Ahmed-Gurey")
    work_district = fields.Char(string="Work District", default="Ahmed-Dhagah")
    department = fields.Selection([('administration', 'Administration'), ('teacher', 'Teachers'),
                                   ('other_staff', 'Other Staff')], string="Department")
    position = fields.Char(string="Position")

    teacher_address = fields.Char(string="Teacher Address")
    teacher_contact = fields.Char(string="Teacher's Contact")
    teacher_email = fields.Char(string="Email")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender")
    marital_status = fields.Selection([('single', 'Single'), ('married', 'Married')])
    date_of_birth = fields.Date(string="Date of Birth")
    color = fields.Selection([('red', 'Red'), ('green', 'Green'), ('blue', 'Blue')], string='Color')





class OtherStaff(models.Model):
    _name = 'otherstaff.info'
    _description = 'Other Staff Information'

    name = fields.Char(string="Name")
    role = fields.Char(string="Role")

