{
    'name': 'High School Dashboard',
    'version': '1.0.0',
    'category': 'School',
    'author': 'Ahmed Khamsa',
    'sequence': -10,
    'summary': 'High School Dashboard',
    'description': """High School Stats Dashboard""",
    'depends': ['base','web','project','om_school'],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_view.xml',
    ],
    'demo': [],
    'web': {
        'assets_frontend': {
            'js': [
                'static/src/js/chart.js',
            ],
        },
        'assets_backend': {
            'js': [
                'static/src/js/chart.js',
            ],
        },
    },
    'assets': {
        'web.assets_backend': [
            'custom_dashboard/static/src/js/dashboard.js',
            'custom_dashboard/static/src/css/dashboard.css',
            # 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.2.1/chart.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.8.0/Chart.bundle.js',
        ],
        'web.assets_qweb': [
            'custom_dashboard/static/src/xml/dashboard.xml',
        ],
    },
    'js': [
                'static/src/js/Chart.js',
            ],
    'qweb': ['/static/src/xml/dashboard.xml'],
    'application': True,
    'installable': True,
    'auto_install': False,
    'License': 'LGPL-3',
}