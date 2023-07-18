from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError

# configuration methods such as academic year and etc

class SchoolConfiguration(models.Model):
    _name = 'school.configuration'
    _description = 'School Configuration'

    division = fields.Char(string="Division")



class AcademicYear(models.Model):
    _name = 'schoolacademic.year'
    _description = 'Academic Year'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _sequence = 'sequence'
    _order = "date_start desc"

    name = fields.Char(string="Name", tracking=True)
    code = fields.Char(string="Code", tracking=True)
    date_start = fields.Date('Term I Start Date', required=True, help='Starting date of academic year')
    date_stop = fields.Date('Term II End Date', required=True, help='Ending of academic year')
    term_start = fields.Date('Term II Start Date', required=True)
    term_end = fields.Date('Term I End Date', required=True)
    sequence = fields.Integer(string="Sequence")
    current = fields.Boolean(string="Current", tracking=True)
    term_structure = fields.Selection([('two_terms', 'Two Terms'), ('three_terms', 'Three Terms'),
                                       ('other', 'Other')], string="Term Structure", default="two_terms")
    term_one_month_ids = fields.One2many('schoolacademic.month', 'year_id', 'Term I Months',
                                         help="Related Academic months")
    state = fields.Selection([('not_shifted', 'Standards are not Shifted'),
                              ('shifted', 'Standards are Shifted')], default="not_shifted")



    def generate_academicmonth(self):
        """Generate academic months."""
        interval = 1
        month_obj = self.env['schoolacademic.month']
        for rec in self:
            start_date = rec.date_start
            while start_date < rec.date_stop:
                end_date = start_date + relativedelta(months=interval, days=-1)
                if end_date > rec.date_stop:
                    end_date = rec.date_stop
                month_obj.create({
                    'name': start_date.strftime('%B'),
                    'code': start_date.strftime('%m/%Y'),
                    'date_start': start_date,
                    'date_stop': end_date,
                    'year_id': rec.id,
                })
                start_date = start_date + relativedelta(months=interval)


    def standard_shift(self):
        # Archive all records in admissions
        applications = self.env['school.applicationregister'].search([])
        for rec in applications:
            rec.write({'active': False})

        timetable = self.env['school.timetable'].search([])
        for rec in timetable:
            rec.write({'active': False})

        student_infos_form_four = self.env['student.info'].search([('standard.name', '=', 'Form Four')])
        alumni_model = self.env['school.alumni']
        for student in student_infos_form_four:
            student.reference_ids.unlink()
            student.active = False
            alumni_model.create({
                'name': student.name,
                'gender': student.gender,
                'date_of_birth': student.date_of_birth,
                'standard': student.standard.id,
                'school_class': student.school_class.id,
                'address_one': student.address_one,
                'district': student.district,
                'city': student.city,
                'addmission_date': student.addmission_date,
                'image': student.image,
                'student_id': student.student_id,
                'parent_name': student.parent_name,
                'phone': student.phone,
                'relation': student.relation,
                'reference_ids': [(0, 0, {'parent_name': ref.parent_name, 'phone': ref.phone, 'relation': ref.relation}) for ref in
                                  student.reference_ids],
                'academic_year': student.academic_year.id
            })

        # Update students in Form Three to Form Four
        student_infos_form_three = self.env['student.info'].search([('standard.name', '=', 'Form Three')])
        form_four = self.env['school.standards'].search([('name', '=', 'Form Four')], limit=1)
        student_infos_form_three.write({'standard': form_four.id})
        student_infos_form_three._onchange_standard()

        # Update students in Form Two to Form Three
        student_infos_form_two = self.env['student.info'].search([('standard.name', '=', 'Form Two')])
        form_three = self.env['school.standards'].search([('name', '=', 'Form Three')], limit=1)
        student_infos_form_two.write({'standard': form_three.id})
        student_infos_form_two._onchange_standard()

        # Update students in Form One to Form Two
        student_infos_form_one = self.env['student.info'].search([('standard.name', '=', 'Form One')])
        form_two = self.env['school.standards'].search([('name', '=', 'Form Two')], limit=1)
        student_infos_form_one.write({'standard': form_two.id})
        student_infos_form_one._onchange_standard()

        # #this is for school class division standards shifting
        # # Update students in Form Three to Form Four
        # class_divisions_form_three = self.env['school.class.division'].search([('class_id.name', '=', 'Form Three')])
        # class_four = self.env['school.standards'].search([('name', '=', 'Form Four')], limit=1)
        # class_divisions_form_three.write({'class_id': class_four.id})
        #
        # # Update students in Form Two to Form Three
        # class_divisions_form_two = self.env['school.class.division'].search([('class_id.name', '=', 'Form Two')])
        # class_three = self.env['school.standards'].search([('name', '=', 'Form Three')], limit=1)
        # class_divisions_form_two.write({'class_id': class_three.id})
        #
        # # Update students in Form One to Form Two
        # class_divisions_form_one = self.env['school.class.division'].search([('class_id.name', '=', 'Form One')])
        # class_two = self.env['school.standards'].search([('name', '=', 'Form Two')], limit=1)
        # class_divisions_form_one.write({'class_id': class_two.id})


        self.write({'state': 'shifted'})






    def set_to_current_academicyear(self):
        current_year = self.search([('current', '=', True)])
        # if not current_year:
        #     raise ValidationError(_("There is no chosen academic year"))
        current_year.write({'current': False})
        self.write({'current': True})

    @api.constrains('current')
    def check_current_year(self):
        '''Constraint on active current year'''
        current_year_rec = self.search_count([('current', '=', True)])
        if current_year_rec >= 2:
            raise ValidationError(_(
                "Error! You cannot set two current year active!"))



class AcademicMonth(models.Model):
    _name = "schoolacademic.month"
    _description = "Academic Month"
    # _order = "date_start"

    name = fields.Char('Name', required=True, help='Name')
    code = fields.Char('Code', required=True, help='Code')
    date_start = fields.Date('Start of Period', required=True, help='Start date')
    date_stop = fields.Date('End of Period', required=True, help='End Date')
    year_id = fields.Many2one('schoolacademic.year', 'Academic Year', required=True, help="Related academic year ")



class SubjectTeacher(models.Model):
    _name = 'subject.teacher'
    _description = 'Subject Teacher'

    subject_id = fields.Many2one('school.subject', string="Current Subject")
    teachers = fields.Many2one('teacher.info', string="Subject Teachers")
    working_shift = fields.Selection([('morning', 'Morning'), ('afternoont', 'Afternoon')], string="Working Shift")


class SchoolSubject(models.Model):
    _name = 'school.subject'
    _description = 'School Subjects'

    name = fields.Char(string="Subject Name")
    code = fields.Char(string="Code")
    minimum_marks = fields.Integer(string="Minimum Marks", default=0)
    maximum_marks = fields.Integer(string="Maximum Marks", default=100)
    teacher_ids = fields.One2many('subject.teacher', 'subject_id', string="Teacher Names")





class SchoolStandard(models.Model):
    _name = 'school.standards'
    _description = 'School Standards'

    name = fields.Char(string="Standard Name")
    sequence = fields.Integer(string="Sequence")
    code = fields.Char(string="Code")
    division_ids = fields.One2many('school.division', 'standard_id', string="Divisions")


class SchoolDivision(models.Model):
    _name = 'school.division'
    _description = 'School Divisions'

    name = fields.Char(string="Class Name")
    code = fields.Char(string="Class Code")
    standard_id = fields.Many2one('school.standards', string="Standard")


class SchoolInformation(models.Model):
    _name = 'school.info'
    _description = 'School Information'

    name = fields.Char(string="School Name")
    code = fields.Char(string="Code")
    address_one = fields.Char(string="Address")
    district = fields.Selection([('ahmed_dhagah', 'Ahmed-Dhagah'), ('thirtyfirst_may', '31 May'),
                                 ('mohamoud_haybe', 'Mohamoud Haybe'), ('twentysix_june', '26 June'),
                                 ('gacan_libah', 'Gacan Libaah'), ('mohamed_moge', 'Mohamed Moge'),
                                 ('ibrahin_kodbur', 'Ibrahin Kodbur'), ('macalin_harun', 'Macalin Harun')],
                                string="District", default="ahmed_dhagah")
    city = fields.Char(default="Hargeisa")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    student_age_required = fields.Char(string="Student Admission Age Required", default="12")
    language = fields.Char(string="Medium Language", default="Somali")
    teachers_total = fields.Char(string="Total Number of Teachers")
    principal = fields.Char(string="Principal")
    school_standards = fields.Many2many('school.standards', string="School Standards")


class SchoolExamType(models.Model):
    _name = 'school.exam.type'
    _description = 'School Exam Type'

    name = fields.Char(string='Name', required=True)
    school_class_division_wise = fields.Selection(
        [('monthly', 'Monthly'), ('bimonthly', 'Bi-monthly'), ('midterm', 'Mid-Term'),
         ('final', 'Final Exam (Exam that promotes students to the next class)')
         ],
        string='Exam Type', default='class')
    school_class_division_scope = fields.Selection([('school', 'School'), ('standard', 'Standard'),
                                                    ('division', 'Division')], string='Exam Scope',
                                                   default='school')
    school = fields.Many2one('school.info', string="School",
                             default=lambda self: self.env['school.info'].search([], limit=1).id)

