from odoo import api, fields, models, _


class CustomDashboard(models.Model):
    _name = 'student.info.dashboard'
    _description = 'Student Dashboard'



class StudentInfoDashboard(models.Model):
    _inherit = 'student.info'

    @api.model
    def get_student_stats(self):
        student_data = self.env['student.info'].search([])
        total_students = len(student_data)
        alumni_data = self.env['school.alumni'].search([])
        total_alumni = len(alumni_data)
        male_students = len(student_data.filtered(lambda r: r.gender == 'male'))
        female_students = len(student_data.filtered(lambda r: r.gender == 'female'))
        # avg_age = "{:.3f}".format(sum(student_data.mapped('age')) / total_students)
        gender_data = {'male': male_students, 'female': female_students}
        standards = self.env['school.standards'].search([])
        standard_student_count = []
        for standard in standards:
            students = self.search([('standard', '=', standard.id)])
            student_count = len(students)
            standard_student_count.append((standard.name, student_count))
        # Count students per academic year
        academic_year_data = self.env['schoolacademic.year'].search([])
        academic_year_student_count = []
        for academic_year in academic_year_data:
            students = self.search([('academic_year', '=', academic_year.id)])
            student_count = len(students)
            academic_year_student_count.append((academic_year.name, student_count))
        return {'total_students': total_students, 'gender_data': gender_data, 'male_students': male_students,
                'female_students': female_students, 'total_alumni': total_alumni,
                'standard_student_count': standard_student_count, 'academic_year_student_count': academic_year_student_count,}

    @api.model
    def get_gender_distribution(self):
        student_data = self.env['student.info'].search([])
        male_count = len(student_data.filtered(lambda r: r.gender == 'male'))
        female_count = len(student_data.filtered(lambda r: r.gender == 'female'))
        data = {
            'male': male_count,
            'female': female_count
        }
        return data






