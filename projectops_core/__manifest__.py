{
    'name': 'ProjectOps',
    'version': '19.0.1.0.0',
    'summary': 'Project management and business operations',
    'description': """
        ProjectOps provides integrated project delivery management,
        team assignments, worklog and expense approvals, project cost tracking,
        billing records, and project reporting for Keradion Technology.
    """,
    'category': 'Project',
    'author': 'Keradion Technology',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'project',
    ],
    'data': [
        'security/projectops_security.xml',
        'security/ir.model.access.csv',
        'views/project_project_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
}
