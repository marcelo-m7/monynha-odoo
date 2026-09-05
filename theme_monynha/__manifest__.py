{
    "name": "Monynha Theme",
    "summary": "Monynha Softwares brutalist-digital identity for Odoo Website",
    "version": "19.0.1.0.0",
    "category": "Theme/Creative",
    "sequence": 120,
    "author": "Monynha Softwares",
    "website": "https://monynha.com",
    "license": "LGPL-3",
    "depends": ["theme_common", "website"],
    "data": [
        "data/ir_asset.xml",
        "views/snippets.xml",
    ],
    "images": ["static/description/theme_monynha.svg"],
    "images_preview_theme": {},
    "assets": {
        "web.assets_frontend": [
            "theme_monynha/static/src/scss/components.scss",
            "theme_monynha/static/src/scss/snippets.scss",
            "theme_monynha/static/src/scss/website.scss",
        ],
    },
    "installable": True,
    "application": False,
}
