from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SchoolExam(models.Model):
    _name = 'school.exam'
    _description = 'School Exam'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', default='New')
    class_id = fields.Many2one('school.standards', string='Standard')
    division_id = fields.Many2one('school.division', string='Division')
    exam_type = fields.Many2one('school.exam.type', string='Type',
                                required=True)
    school_class_division_wise = fields.Selection(
        [('school', 'School'), ('class', 'Class'), ('division', 'Division')],
        related='exam_type.school_class_division_wise',
        string='School/Class/Division Wise')
    class_division_hider = fields.Char(string='Class Division Hider')
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    subject_line = fields.One2many('school.subject.line', 'exam_id',
                                   string='Subjects')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('ongoing', 'On Going'),
         ('close', 'Closed'),
         ('cancel', 'Canceled')],
        default='draft')
    academic_year = fields.Many2one('schoolacademic.year',
                                    string='Academic Year',
                                    store=True)
    school = fields.Many2one('school.info', string="School",
                             default=lambda self: self.env['school.info'].search([], limit=1).id)

    @api.model
    def create(self, vals):
        res = super(SchoolExam, self).create(vals)
        if res.division_id:
            res.class_id = res.division_id.class_id.id
        return res

    # @api.onchange('class_division_hider')
    # def onchange_class_division_hider(self):
    #     self.school_class_division_wise = 'school'

    @api.constrains('start_date', 'end_date')
    def check_dates(self):
        for rec in self:
            if rec.start_date > rec.end_date:
                raise ValidationError(
                    _("Start date must be Anterior to end date"))

    def close_exam(self):
        self.state = 'close'

    def cancel_exam(self):
        self.state = 'cancel'

    def confirm_exam(self):
        if len(self.subject_line) < 1:
            raise UserError(_('Please Add Subjects'))
        name = str(self.exam_type.name) + '-' + str(self.start_date)[0:10]
        if self.division_id:
            name = name + ' (' + str(self.division_id.name) + ')'
        elif self.class_id:
            name = name + ' (' + str(self.class_id.name) + ')'
        self.name = name
        self.state = 'ongoing'


class SubjectLine(models.Model):
    _name = 'school.subject.line'
    _description = 'Subject Line'

    subject_id = fields.Many2one('school.subject', string='Subject',
                                 required=True)
    date = fields.Date(string='Date', required=True)
    time_from = fields.Float(string='Time From', required=True)
    time_to = fields.Float(string='Time To', required=True)
    mark = fields.Integer(string='Mark')
    exam_id = fields.Many2one('school.exam', string='Exam')
    school = fields.Many2one('school.info', string="School",
                             default=lambda self: self.env['school.info'].search([], limit=1).id)



class SchoolExamValuation(models.Model):
    _name = 'school.exam.valuation'
    _description = "Exam Valuation"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', default='New')
    exam_id = fields.Many2one('school.exam', string='Exam', required=True)
    class_id = fields.Many2one('school.standards', string='Standard', required=True)
    division_id = fields.Many2one('school.class.division', string='Standard Division', required=True)
    teachers_id = fields.Many2one('teacher.info', string='Evaluator')
    mark = fields.Float(string='Max Mark', required=True, default=100)
    pass_mark = fields.Float(string='Pass Mark', required=True, default=50)
    state = fields.Selection([('draft', 'Draft'), ('completed', 'Completed'),
                              ('cancel', 'Canceled')], default='draft')
    valuation_line = fields.One2many('studentsexam.valuation.line', 'valuation_id',
                                     string='Students')
    subject_id = fields.Many2one('school.subject', string='Subject', required=True)
    mark_sheet_created = fields.Boolean(string='Mark sheet Created')
    date = fields.Date(string='Date', default=fields.Date.today)
    academic_year = fields.Many2one('schoolacademic.year', string='Academic Year', store=True)
    school = fields.Many2one('school.info', string="School",
                             default=lambda self: self.env['school.info'].search([], limit=1).id)

    @api.onchange('class_id')
    def onchange_class_id(self):
        domain = []
        if self.division_id.class_id != self.class_id:
            self.division_id = ''
        if self.class_id:
            domain = [('class_id', '=', self.class_id.id)]
        return {'domain': {'division_id': domain}}

    @api.onchange('pass_mark')
    def onchange_pass_mark(self):
        if self.pass_mark > self.mark:
            raise UserError(_('Pass mark must be less than Max Mark'))
        for records in self.valuation_line:
            records.pass_or_fail = True if records.mark_scored >= self.pass_mark else False

    @api.onchange('exam_id', 'subject_id')
    def onchange_exam_id(self):
        if self.exam_id:
            if self.exam_id.division_id:
                self.class_id = self.exam_id.class_id
                self.division_id = self.exam_id.division_id
            elif self.exam_id.class_id:
                self.class_id = self.exam_id.class_id
            else:
                self.class_id = ''
                self.division_id = ''
            self.mark = ''
            if self.subject_id:
                for sub in self.exam_id.subject_line:
                    if sub.subject_id.id == self.subject_id.id:
                        if sub.mark:
                            self.mark = sub.mark
        domain = []
        subjects = self.exam_id.subject_line
        for items in subjects:
            domain.append(items.subject_id.id)
        return {'domain': {'subject_id': [('id', 'in', domain)]}}

    def create_mark_sheet(self):
        valuation_line_obj = self.env['studentsexam.valuation.line']
        students = self.division_id.student_ids
        if len(students) < 1:
            raise UserError(_('There are no students in this Division'))
        for student in students:
            data = {
                'student_id': student.id,
                'student_name': student.name,
                'valuation_id': self.id,
            }
            valuation_line_obj.create(data)
        self.mark_sheet_created = True

    @api.model
    def create(self, vals):
        res = super(SchoolExamValuation, self).create(vals)
        valuation_obj = self.env['school.exam.valuation']
        search_valuation = valuation_obj.search(
            [('exam_id', '=', res.exam_id.id),
             ('division_id', '=', res.division_id.id),
             ('subject_id', '=', res.subject_id.id), ('state', '!=', 'cancel')])
        if len(search_valuation) > 1:
            raise UserError(
                _(
                    'Valuation Sheet for \n Subject --> %s \nDivision --> %s \nExam --> %s \n is already created') % (
                    res.subject_id.name, res.division_id.name,
                    res.exam_id.name))
        return res

    def valuation_completed(self):
        self.name = str(self.exam_id.exam_type.name) + '-' + str(
            self.exam_id.start_date)[0:10] + ' (' + str(
            self.division_id.name) + ')'
        result_obj = self.env['school.exam.results']
        result_line_obj = self.env['exam.results.subject.line']
        for students in self.valuation_line:
            search_result = result_obj.search(
                [('exam_id', '=', self.exam_id.id),
                 ('division_id', '=', self.division_id.id),
                 ('student_id', '=', students.student_id.id)])
            if len(search_result) < 1:
                result_data = {
                    'name': self.name,
                    'exam_id': self.exam_id.id,
                    'class_id': self.class_id.id,
                    'division_id': self.division_id.id,
                    'student_id': students.student_id.id,
                    'student_name': students.student_id.name,
                }
                result = result_obj.create(result_data)
                result_line_data = {
                    'name': self.name,
                    'subject_id': self.subject_id.id,
                    'max_mark': self.mark,
                    'pass_mark': self.pass_mark,
                    'mark_scored': students.mark_scored,
                    'pass_or_fail': students.pass_or_fail,
                    'result_id': result.id,
                    'exam_id': self.exam_id.id,
                    'class_id': self.class_id.id,
                    'division_id': self.division_id.id,
                    'student_id': students.student_id.id,
                    'student_name': students.student_id.name,
                }
                result_line_obj.create(result_line_data)
            else:
                result_line_data = {
                    'subject_id': self.subject_id.id,
                    'max_mark': self.mark,
                    'pass_mark': self.pass_mark,
                    'mark_scored': students.mark_scored,
                    'pass_or_fail': students.pass_or_fail,
                    'result_id': search_result.id,
                    'exam_id': self.exam_id.id,
                    'class_id': self.class_id.id,
                    'division_id': self.division_id.id,
                    'student_id': students.student_id.id,
                    'student_name': students.student_id.name,
                }
                result_line_obj.create(result_line_data)
        self.state = 'completed'

    def set_to_draft(self):
        result_line_obj = self.env['exam.results.subject.line']
        result_obj = self.env['school.exam.results']
        for students in self.valuation_line:
            search_result = result_obj.search(
                [('exam_id', '=', self.exam_id.id),
                 ('division_id', '=', self.division_id.id),
                 ('student_id', '=', students.student_id.id)])
            search_result_line = result_line_obj.search(
                [('result_id', '=', search_result.id),
                 ('subject_id', '=', self.subject_id.id)])
            search_result_line.unlink()
        self.state = 'draft'

    def valuation_canceled(self):
        self.state = 'cancel'


class StudentsExamValuationLine(models.Model):
    _name = 'studentsexam.valuation.line'
    _description = 'Students Exam Valuation Line'
#
    student_id = fields.Many2one('student.info', string='Students')
    student_name = fields.Char(string='Students')
    mark_scored = fields.Float(string='Mark')
    pass_or_fail = fields.Boolean(string='Pass/Fail')
    valuation_id = fields.Many2one('school.exam.valuation',
                                   string='Valuation Id')
    school = fields.Many2one('school.info', string="School",
                             default=lambda self: self.env['school.info'].search([], limit=1).id)

    @api.onchange('mark_scored', 'pass_or_fail')
    def onchange_mark_scored(self):
        if self.mark_scored > self.valuation_id.mark:
            raise UserError(_('Mark Scored must be less than Max Mark'))
        if self.mark_scored >= self.valuation_id.pass_mark:
            self.pass_or_fail = True
        else:
            self.pass_or_fail = False



class SchoolExamResults(models.Model):
    _name = 'school.exam.results'
    _description = 'Exam Results'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name')
    exam_id = fields.Many2one('school.exam', string='Exam')
    class_id = fields.Many2one('school.standards', string='Class')
    division_id = fields.Many2one('school.class.division', string='Division')
    student_id = fields.Many2one('student.info', string='Student')
    student_name = fields.Char(string='Student')
    subject_line = fields.One2many('exam.results.subject.line', 'result_id',
                                   string='Subjects')
    academic_year = fields.Many2one('schoolacademic.year',
                                    string='Academic Year',
                                    # related='division_id.academic_year_id',
                                    store=True)
    school = fields.Many2one('school.info', string="School",
                             default=lambda self: self.env['school.info'].search([], limit=1).id)
    total_pass_mark = fields.Float(string='Total Pass Mark', store=True,
                                   readonly=True, compute='_total_marks_all')
    total_max_mark = fields.Float(string='Total Max Mark', store=True,
                                  readonly=True, compute='_total_marks_all')
    total_mark_scored = fields.Float(string='Total Marks Scored', store=True,
                                     readonly=True, compute='_total_marks_all')
    overall_pass = fields.Boolean(string='Overall Pass/Fail', store=True,
                                  readonly=True, compute='_total_marks_all')
    active_id = fields.Boolean()

    @api.depends('subject_line.mark_scored')
    def _total_marks_all(self):
        for results in self:
            total_pass_mark = 0
            total_max_mark = 0
            total_mark_scored = 0
            overall_pass = True
            for subjects in results.subject_line:
                total_pass_mark += subjects.pass_mark
                total_max_mark += subjects.max_mark
                total_mark_scored += subjects.mark_scored
                if not subjects.pass_or_fail:
                    overall_pass = False
            results.total_pass_mark = total_pass_mark
            results.total_max_mark = total_max_mark
            results.total_mark_scored = total_mark_scored
            results.overall_pass = overall_pass


class ResultsSubjectLine(models.Model):
    _name = 'exam.results.subject.line'
    _description = 'Results Subject Line'

    name = fields.Char(string='Name')
    subject_id = fields.Many2one('school.subject', string='Subject')
    max_mark = fields.Float(string='Max Mark')
    pass_mark = fields.Float(string='Pass Mark')
    mark_scored = fields.Float(string='Mark Scored')
    pass_or_fail = fields.Boolean(string='Pass/Fail')
    result_id = fields.Many2one('school.exam.results', string='Result Id')
    exam_id = fields.Many2one('school.exam', string='Exam')
    class_id = fields.Many2one('school.standards', string='Class')
    division_id = fields.Many2one('school.class.division', string='Division')
    student_id = fields.Many2one('student.info', string='Student')
    student_name = fields.Char(string='Student')
    academic_year = fields.Many2one('schoolacademic.year',
                                    string='Academic Year',
                                    # related='division_id.academic_year_id',
                                    store=True)
    school = fields.Many2one('school.info', string="School",
                             default=lambda self: self.env['school.info'].search([], limit=1).id)
