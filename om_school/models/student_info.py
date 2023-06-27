from odoo import api, fields, models, _
from dateutil import relativedelta
from datetime import date
from odoo.exceptions import ValidationError, UserError


class StudentInformation(models.Model):
    _name = 'student.info'
    _description = 'Student Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def check_current_year(self):
        '''Method to get default value of logged in Student'''
        res = self.env['schoolacademic.year'].search([('current', '=', True)])
        if not res:
            raise ValidationError(_(
                "There is no current Academic Year defined! Please contact Administator!"))
        return res.id



    name = fields.Char(string="Name", required=True)
    gender = fields.Selection([('male','Male'),('female','Female')], string="Gender")
    date_of_birth = fields.Date(string="Date of Birth")
    age = fields.Integer(string="Age", compute="_compute_age", inverse="_inverse_compute_age",
                         search="_search_age", tracking=True)
    color1 = fields.Integer('Color Index', default=0, help='Color index')
    color2 = fields.Integer(string="Color")
    standard = fields.Many2one('school.standards', string="Standard")
    school_class = fields.Many2one('school.division', string="Class",
                                   domain="[('standard_id', '=', standard)]")
    class_division = fields.Char(string="Class Division")
    address_one = fields.Char(string="Address")
    district = fields.Selection([('ahmed_dhagah', 'Ahmed-Dhagah'), ('thirtyfirst_may', '31 May'),
                                 ('mohamoud_haybe', 'Mohamoud Haybe'), ('twentysix_june', '26 June'),
                                 ('gacan_libah', 'Gacan Libaah'),('mohamed_moge', 'Mohamed Moge'),
                                 ('ibrahin_kodbur', 'Ibrahin Kodbur'), ('macalin_harun', 'Macalin Harun')],
                                string="District")
    city = fields.Char(default="Hargeisa")
    addmission_date = fields.Date(string="Admission Date")
    image = fields.Image(string="Image")
    student_id = fields.Char(string="Student ID")
    parent_name = fields.Char(string="Parent")
    phone = fields.Integer(string="Phone")
    relation = fields.Selection([('father', 'Father'), ('mother', 'Mother')], string="Relation")
    reference_ids = fields.One2many('student.parent', 'reference_id', 'References')
    color = fields.Selection([('red', 'Red'), ('green', 'Green'), ('blue', 'Blue')], string='Color')
    academic_year = fields.Many2one('schoolacademic.year', string="Academic Year", default=check_current_year,
                                    help='Select academic year', tracking=True)
    school = fields.Char(string="School", default="Quule Adan Secondary School")
    application_number = fields.Char('Application Number',
                                     default=lambda self: self._context.get('default_application_number',
                                                                            self.env['ir.sequence'].next_by_code(
                                                                                'school.applicationregister')))
    previous_school_ids = fields.One2many('previous.school', 'previous_sch_id', string="Previous School IDs")
    active = fields.Boolean(default=True)
    class_id = fields.Many2one('school.class.division', string="Class")


    #this function is used to create the sequence of the student id
    @api.model
    def create(self, vals):
        vals['student_id'] = self.env['ir.sequence'].next_by_code('student.info')
        return super(StudentInformation, self).create(vals)

    @api.depends('standard', 'school_class')
    def _compute_class_division(self):
        for rec in self:
            rec.class_division = f"{rec.standard.name} - {rec.school_class.name}"

    @api.onchange('standard')
    def _onchange_standard(self):
        for rec in self:
            rec.class_division = False
            if rec.standard:
                rec.class_division = f"{rec.standard.name} - {rec.school_class.name}"

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








class StudentReference(models.Model):
    ''' Defining a student reference information '''

    _name = "student.parent"
    _description = "Student Reference"

    reference_id = fields.Many2one('student.info', string="Parent",
                help='Student Parent', ondelete="cascade")
    parent_name = fields.Char(string="Parent Name")
    phone = fields.Char('Phone', required=True,  help='Student phone')
    relation = fields.Selection([('father', 'Father'), ('mother', 'Mother')],
                'Relation',  help='parent relation')
    parent_id = fields.Many2one('school.applicationregister', string="Parent",
                                help='Student Parent')


class PreviousSchool(models.Model):
    _name = 'previous.school'
    _description = "Student Previous School"


    previous_sch_id = fields.Many2one('student.info', string="Previous School")
    previous_school_id = fields.Many2one('school.applicationregister', string="Previous School")
    name = fields.Char(string="Previous School Name")
    standard = fields.Many2one('school.standards', string="Standard")
    grade = fields.Char(string="Previous School Grade")



class SchoolAlumni(models.Model):
    _name = 'school.alumni'
    _description = 'School Alumni'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender")
    date_of_birth = fields.Date(string="Date of Birth")
    age = fields.Integer(string="Age", compute="_compute_age", inverse="_inverse_compute_age",
                         search="_search_age", tracking=True)
    standard = fields.Many2one('school.standards', string="Standard")
    school_class = fields.Many2one('school.division', string="Class")
    color1 = fields.Integer('Color Index', default=0, help='Color index')
    color2 = fields.Integer(string="Color")
    address_one = fields.Char(string="Address")
    district = fields.Selection([('ahmed_dhagah', 'Ahmed-Dhagah'), ('thirtyfirst_may', '31 May'),
                                 ('mohamoud_haybe', 'Mohamoud Haybe'), ('twentysix_june', '26 June'),
                                 ('gacan_libah', 'Gacan Libaah'), ('mohamed_moge', 'Mohamed Moge'),
                                 ('ibrahin_kodbur', 'Ibrahin Kodbur'), ('macalin_harun', 'Macalin Harun')],
                                string="District")
    city = fields.Char(default="Hargeisa")
    addmission_date = fields.Date(string="Admission Date")
    image = fields.Image(string="Image")
    student_id = fields.Char(string="Student ID")
    parent_name = fields.Char(string="Parent")
    phone = fields.Integer(string="Phone")
    relation = fields.Selection([('father', 'Father'), ('mother', 'Mother')], string="Relation")
    reference_ids = fields.One2many('student.parent', 'reference_id', 'References')
    color = fields.Selection([('red', 'Red'), ('green', 'Green'), ('blue', 'Blue')], string='Color')
    school = fields.Char(string="School", default="Quule Adan Secondary School")
    academic_year = fields.Many2one('schoolacademic.year', string="Academic Year",
                                    help='Select academic year', tracking=True)

    @api.model
    def create(self, vals):
        '''Method to change standard to Alumni'''
        res = super(SchoolAlumni, self).create(vals)
        if res.standard and res.standard.name == 'Form Four':
            res.write({'standard': False})
        return res


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



class SchoolClassDivision(models.Model):
    _name = 'school.class.division'
    _description = "Class room"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    @api.model
    def check_current_year(self):
        '''Method to get default value of logged in Student'''
        res = self.env['schoolacademic.year'].search([('current', '=', True)])
        return res.id

    def view_students(self):
        """Return the list of current students in this class"""
        self.ensure_one()
        students = self.env['student.info'].search([('class_division', '=', self.name)])
        self.student_ids = students
        students_list = students.mapped('id')
        return {
            'domain': [('id', 'in', students_list)],
            'name': _('Students'),
            'view_mode': 'tree,form',
            'res_model': 'student.info',
            'view_id': False,
            'context': {'default_class_id': self.class_id.id},
            'type': 'ir.actions.act_window'
        }

    # def _get_student_count(self):
    #     for rec in self:
    #         rec.student_count = self.env['student.info'].search_count([('class_division', '=', rec.name)])
    #         rec.all_student_count = self.env['student.info'].search_count([
    #             ('class_division', '=', rec.name),
    #             ('academic_year', 'in', self.env['schoolacademic.year'].search([]).ids)
    #         ])

    # def button_update_student_count(self):
    #     self._get_student_count()

    # @api.depends('name')
    # def _get_student_count(self):
    #     for rec in self:
    #         academic_years = self.env['schoolacademic.year'].search([])
    #         student_count = 0
    #         for year in academic_years:
    #             count = self.env['student.info'].search_count(
    #                 [('class_division', '=', rec.name)])
    #             student_count += count
    #         rec.student_count = student_count

    @api.depends('division_id')
    def _get_student_count(self):
        for record in self:
            count = self.env['student.info'].search_count([('class_division', '=', record.name)])
            record.student_count = count

    name = fields.Char(string='Name', readonly=True, compute='_compute_class_division')
    actual_strength = fields.Integer(string='Class Strength',
                                     help="Total strength of the class")
    teacher_id = fields.Many2one('teacher.info', string='Form Master',
                                 help="Class teacher/Faculty")
    academic_year = fields.Many2one('schoolacademic.year',
                                       string='Academic Year',default=check_current_year,
                                       help="Select the Academic Year",
                                       required=True)
    class_id = fields.Many2one('school.standards', string='Standard', required=True,
                               help="Select the Class")
    division_id = fields.Many2one('school.division', string='Division',
                                  required=True, domain="[('standard_id','=',class_id)]",
                                  help="Select the Division")
    student_ids = fields.One2many('student.info', 'class_id', string='Students')
    # amenities_ids = fields.One2many('education.class.amenities', 'class_id',
    #                                 string='Amenities')
    student_count = fields.Integer(string='Students Count', compute='_get_student_count')
    # all_student_count = fields.Integer(string='All Students Count')


    @api.depends('class_id', 'division_id')
    def _compute_class_division(self):
        for rec in self:
            rec.name = f"{rec.class_id.name} - {rec.division_id.name}"

    @api.onchange('class_id')
    def _onchange_class_id(self):
        self.name = f"{self.class_id.name} - {self.division_id.name}"



    # def view_students(self):
    #     """Return the list of current students in this class"""
    #     self.ensure_one()
    #     students = self.env['student.info'].search(
    #         [('standard', '=', self.class_id.id), ('school_class', '=', self.division_id.id)])
    #     self.student_ids = students
    #     return {
    #         'domain': [('id', 'in', students.ids)],
    #         'name': _('Students'),
    #         'view_mode': 'tree,form',
    #         'res_model': 'student.info',
    #         'view_id': False,
    #         'context': {'default_class_id': self.class_id.id},
    #         'type': 'ir.actions.act_window'
    #     }
    #
    # def _get_student_count(self):
    #     """Return the number of students in the class"""
    #     for rec in self:
    #         students = self.env['student.info'].search(
    #             [('standard', '=', rec.class_id.id), ('school_class', '=', rec.division_id.id)])
    #         student_count = len(students) if students else 0
    #         rec.update({
    #             'student_count': student_count,
    #             'student_ids': [(6, 0, students.ids)],
    #         })

    #
    # @api.constrains('actual_strength')
    # def validate_strength(self):
    #     """Return Validation error if
    #         the students strength is not a non-zero number"""
    #     for rec in self:
    #         if rec.actual_strength <= 0:
    #             raise ValidationError(_('Strength must be a Non-Zero value'))





class SchoolStudentsAttendance(models.Model):
    _name = 'school.attendance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Students Attendance'

    name = fields.Char(string='Name', default='New')
    class_division = fields.Many2one('school.class.division', string="Class Division")
    class_id = fields.Many2one('school.standards', string='Class')
    division_id = fields.Many2one('school.class.division', string='Division',
                                  required=True)
    date = fields.Date(string='Date', default=fields.Date.today, required=True)
    attendance_line = fields.One2many('school.attendance.line',
                                      'attendance_id', string='Attendance Line')
    attendance_created = fields.Boolean(string='Attendance Created')
    all_marked_morning = fields.Boolean(
        string='All students are present in the morning')
    all_marked_afternoon = fields.Boolean(
        string='All students are present in the afternoon')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                             default='draft')
    school = fields.Many2one('school.info', string="School",
                             default=lambda self: self.env['school.info'].search([], limit=1).id)
    academic_year = fields.Many2one('schoolacademic.year',
                                    string='Academic Year',
                                    # related='division_id.academic_year_id',
                                    store=True)
    faculty_id = fields.Many2one('teacher.info', string='Teacher')

    @api.model
    def create(self, vals):
        res = super(SchoolStudentsAttendance, self).create(vals)
        res.class_id = res.division_id.class_id.id
        attendance_obj = self.env['school.attendance']
        already_created_attendance = attendance_obj.search(
            [('division_id', '=', res.division_id.id), ('date', '=', res.date),
             ('school', '=', res.school.id)])
        if len(already_created_attendance) > 1:
            raise ValidationError(
                _('Attendance register of %s is already created on "%s"', ) % (
                    res.division_id.name, res.date))
        return res

    def create_attendance_line(self):
        self.name = str(self.date)
        attendance_line_obj = self.env['school.attendance.line']
        students = self.division_id.student_ids
        if len(students) < 1:
            raise UserError(_('There are no students in this Division'))
        for student in students:
            data = {
                'name': self.name,
                'attendance_id': self.id,
                'student_id': student.id,
                'student_name': student.name,
                'class_id': self.division_id.class_id.id,
                'division_id': self.division_id.id,
                'date': self.date,
            }
            attendance_line_obj.create(data)
        self.attendance_created = True

    def mark_all_present_morning(self):
        for records in self.attendance_line:
            records.present_morning = True
        self.all_marked_morning = True

    def un_mark_all_present_morning(self):
        for records in self.attendance_line:
            records.present_morning = False
        self.all_marked_morning = False

    def mark_all_present_afternoon(self):
        for records in self.attendance_line:
            records.present_afternoon = True
        self.all_marked_afternoon = True

    def un_mark_all_present_afternoon(self):
        for records in self.attendance_line:
            records.present_afternoon = False
        self.all_marked_afternoon = False

    def attendance_done(self):
        for records in self.attendance_line:
            records.state = 'done'
            if not records.present_morning and not records.present_afternoon:
                records.full_day_absent = 1
            elif not records.present_morning:
                records.half_day_absent = 1
            elif not records.present_afternoon:
                records.half_day_absent = 1
        self.state = 'done'

    def set_to_draft(self):
        for records in self.attendance_line:
            records.state = 'draft'
        self.state = 'draft'


class EducationAttendanceLine(models.Model):
    _name = 'school.attendance.line'
    _description = 'Attendance Lines'

    name = fields.Char(string='Name')
    attendance_id = fields.Many2one('school.attendance',
                                    string='Attendance Id')
    student_id = fields.Many2one('student.info', string='Student')
    student_name = fields.Char(string='Student', related='student_id.name',
                               store=True)
    class_id = fields.Many2one('school.standards', string='Class', required=True)
    division_id = fields.Many2one('school.class.division', string='Division',
                                  required=True)
    date = fields.Date(string='Date', required=True)
    present_morning = fields.Boolean(string='Morning')
    present_afternoon = fields.Boolean(string='After Noon')
    full_day_absent = fields.Integer(string='Full Day')
    half_day_absent = fields.Integer(string='Half Day')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                             string='State', default='draft')
    school = fields.Many2one('school.info', string="School",
                             default=lambda self: self.env['school.info'].search([], limit=1).id)
    academic_year = fields.Many2one('schoolacademic.year',
                                    string='Academic Year',
                                    # related='division_id.academic_year_id',
                                    store=True)



class SchoolTimetable(models.Model):
    _name = 'school.timetable'
    _description = 'School Timetable'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def create(self, vals):
        """Return the name as a str of class + division"""
        class_id = self.env['school.standards'].browse(vals['class_id'])
        division_id = self.env['school.division'].browse(vals['division_id'])
        academic_year = self.env['schoolacademic.year'].browse(vals['academic_year'])
        name = str(class_id.name + ' - ' + division_id.name + '/' + academic_year.name)
        vals['name'] = name
        return super(SchoolTimetable, self).create(vals)

    @api.model
    def check_current_year(self):
        '''Method to get default value of logged in Student'''
        res = self.env['schoolacademic.year'].search([('current', '=', True)])
        if not res:
            raise ValidationError(_(
                "There is no current Academic Year defined! Please contact Administator!"))
        return res.id

    active = fields.Boolean('Active', default=True)
    name = fields.Char(string="Class Division")
    class_id = fields.Many2one('school.standards', string='Standard', required=True,
                               help="Select the Class")
    division_id = fields.Many2one('school.division',string="Class", domain="[('standard_id','=',class_id)]",)
    academic_year = fields.Many2one('schoolacademic.year', string="Academic Year", default=check_current_year,
                                    help='Select academic year', tracking=True)
    school = fields.Char(string="School")
    # school = fields.Many2one('school.info', string="School",
    #                          default=lambda self: self.env['school.info'].search([], limit=1).id)
    timetable_mon = fields.One2many('school.timetable.schedule',
                                    'timetable_id',
                                    domain=[('week_day', '=', '0')])
    timetable_tue = fields.One2many('school.timetable.schedule',
                                    'timetable_id',
                                    domain=[('week_day', '=', '1')])
    timetable_wed = fields.One2many('school.timetable.schedule',
                                    'timetable_id',
                                    domain=[('week_day', '=', '2')])
    timetable_thur = fields.One2many('school.timetable.schedule',
                                     'timetable_id',
                                     domain=[('week_day', '=', '3')])
    timetable_fri = fields.One2many('school.timetable.schedule',
                                    'timetable_id',
                                    domain=[('week_day', '=', '4')])
    timetable_sat = fields.One2many('school.timetable.schedule',
                                    'timetable_id',
                                    domain=[('week_day', '=', '5')])
    timetable_sun = fields.One2many('school.timetable.schedule',
                                    'timetable_id',
                                    domain=[('week_day', '=', '6')])

    # @api.depends('standard_class', 'academic_year')
    # def _compute_name(self):
    #     for record in self:
    #         name = f"{record.standard_class.name} - {record.academic_year.name}"
    #         record.name = name




class SchoolTimeTableSchedule(models.Model):
    _name = 'school.timetable.schedule'
    _description = 'Timetable Schedule'
    _rec_name = 'period_id'

    period_id = fields.Many2one('school.timetable.period', string="Period",
                                required=True, )
    time_from = fields.Float(string='From', required=True,
                             index=True, help="Start and End time of Period.")
    time_till = fields.Float(string='Till', required=True)
    subject = fields.Many2one('school.subject', string='Subjects',
                              required=True)
    faculty_id = fields.Many2one('teacher.info', string='Teacher',
                                 required=True)
    week_day = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ], 'Week', required=True)
    timetable_id = fields.Many2one('school.timetable', required=True, )
    division_id = fields.Many2one('school.division', string="Class")

    @api.model
    def create(self, vals):
        """Automatically stores division details fetched from timetable"""
        res = super(SchoolTimeTableSchedule, self).create(vals)
        res.division_id = res.timetable_id.division_id.id
        return res

    @api.onchange('period_id')
    def onchange_period_id(self):
        """Gets the start and end time of the period"""
        for i in self:
            i.time_from = i.period_id.time_from
            i.time_till = i.period_id.time_to



class TimetablePeriod(models.Model):
    _name = 'school.timetable.period'
    _description = 'Timetable Period'

    name = fields.Char(string="Name", required=True, )
    time_from = fields.Float(string='From', required=True,
                             index=True, help="Start and End time of Period.")
    time_to = fields.Float(string='To', required=True)














