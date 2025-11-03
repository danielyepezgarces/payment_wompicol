{
    'name': 'Wompi Payment Acquirer',
    'version': '19.0.1.0.0',
    'author': 'Lintec Tecnología',
    'category': 'Accounting/Payment Providers',
    'summary': 'Payment Acquirer: Wompi Colombia Implementation',
    'description': """Wompi Colombia payment acquirer""",
    'depends': ['payment'],
    'data': [
        'views/payment_views.xml',
        'views/payment_wompicol_templates.xml',
        'views/template_modify.xml',
        'data/payment_acquirer_data.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'license': 'MIT',
}
