{
    "name": "Monynha Content",
    "summary": "Structured Work and Blog aggregation for the Monynha website",
    "version": "19.0.1.0.0",
    "category": "Website/Website",
    "author": "Monynha Softwares",
    "website": "https://monynha.com",
    "license": "LGPL-3",
    "depends": ["theme_monynha", "website", "website_blog"],
    "data": [
        "security/ir.model.access.csv",
        "views/work_views.xml",
        "views/work_templates.xml",
        "views/snippets.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "monynha_content/static/src/scss/content.scss",
        ],
    },
    "installable": True,
    "application": False,
}
