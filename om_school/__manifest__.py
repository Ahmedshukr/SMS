{
    'name': 'School Management',
    'version': '1.0.0',
    'category': 'School',
    'author': 'Ahmed Khamsa',
    'sequence': -100,
    'summary': 'School Management System',
    'description': """School Management System""",
    'depends': ['mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/menu.xml',
        'views/school_exam_view.xml',
        'views/school_student_view.xml',
        'views/school_staff_view.xml',
        'views/school_configuration_view.xml',
        'views/school_admission_view.xml',
        'views/school_dashboard_view.xml',
        'views/school_finance_view.xml',
    ],
    'demo': [],
    'application': True,
    'installable': True,
    'auto_install': False,
    'License': 'LGPL-3',
}