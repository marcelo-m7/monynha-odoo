{
    "name": "Monynha Lead Generator",
    "summary": "Interactive website discovery that creates and enriches standard CRM leads",
    "version": "19.0.1.0.0",
    "category": "Sales/CRM",
    "author": "Monynha Softwares",
    "website": "https://monynha.com",
    "license": "LGPL-3",
    "depends": ["crm", "website", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_templates.xml",
        "views/crm_lead_views.xml",
        "views/diagnosis_views.xml",
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "monynha_lead_generator/static/src/scss/lead_generator.scss",
            "monynha_lead_generator/static/src/js/discovery.js",
        ],
    },
    "installable": True,
    "application": False,
}
