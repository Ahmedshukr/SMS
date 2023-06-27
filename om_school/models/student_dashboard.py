from odoo import api, fields, models

class StudentDashboard(models.Model):
    _name = 'student.dashboard'
    _description = 'Student Dashboard'

    student_count = fields.Integer(string='Total Students')
    male_count = fields.Integer(string='Male Students')
    female_count = fields.Integer(string='Female Students')
    avg_age = fields.Float(string='Average Age')
    # district_count = fields.One2many('student.dashboard.district', 'dashboard_id', string='District Counts')

class StudentInfoDashboard(models.Model):
    _inherit = 'student.info'

    @api.model
    def get_student_stats(self):
        student_data = self.env['student.info'].search([])
        total_students = len(student_data)
        male_students = len(student_data.filtered(lambda r: r.gender == 'male'))
        female_students = len(student_data.filtered(lambda r: r.gender == 'female'))
        avg_age = "{:.3f}".format(sum(student_data.mapped('age')) / total_students)
        gender_data = {'male': male_students, 'female': female_students}
        return {'total_students': total_students, 'gender_data': gender_data, 'male_students': male_students, 'female_students': female_students,
                'avg_age': avg_age}



