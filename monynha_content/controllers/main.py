from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request


class MonynhaContentController(http.Controller):
    _PER_PAGE = 12
    _CATALOGUE_TITLES = {
        None: "Work",
        "project": "Projects",
        "case": "Cases",
        "lab": "Labs",
    }

    @staticmethod
    def _positive_int(value, default=1):
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return default
        return parsed if parsed > 0 else default

    @staticmethod
    def _tag_id(value):
        if value in (None, ""):
            return None
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return -1
        return parsed if parsed > 0 else -1

    def _render_catalogue(self, *, work_type=None, page=1, tag=None):
        website = request.website
        query = request.env["monynha.content.query"]
        page_number = self._positive_int(page)
        tag_id = self._tag_id(tag)
        total = query.count_works(website, work_type=work_type, tag=tag_id)
        url_args = {"tag": tag_id} if tag_id is not None else {}
        pager = request.website.pager(
            url=request.httprequest.path,
            total=total,
            page=page_number,
            step=self._PER_PAGE,
            url_args=url_args,
        )
        works = query.get_works(
            website,
            work_type=work_type,
            tag=tag_id,
            limit=self._PER_PAGE,
            offset=pager["offset"],
        )
        return request.render(
            "monynha_content.work_index",
            {
                "works": works,
                "work_type": work_type,
                "catalogue_title": self._CATALOGUE_TITLES[work_type],
                "pager": pager,
                "active_tag": tag_id,
            },
        )

    @http.route(
        "/work",
        type="http",
        auth="public",
        website=True,
        sitemap=True,
        methods=["GET"],
    )
    def work_index(self, page=1, tag=None, **kwargs):
        return self._render_catalogue(page=page, tag=tag)

    @http.route(
        "/projects",
        type="http",
        auth="public",
        website=True,
        sitemap=True,
        methods=["GET"],
    )
    def project_index(self, page=1, tag=None, **kwargs):
        return self._render_catalogue(work_type="project", page=page, tag=tag)

    @http.route(
        "/cases",
        type="http",
        auth="public",
        website=True,
        sitemap=True,
        methods=["GET"],
    )
    def case_index(self, page=1, tag=None, **kwargs):
        return self._render_catalogue(work_type="case", page=page, tag=tag)

    @http.route(
        "/labs",
        type="http",
        auth="public",
        website=True,
        sitemap=True,
        methods=["GET"],
    )
    def lab_index(self, page=1, tag=None, **kwargs):
        return self._render_catalogue(work_type="lab", page=page, tag=tag)

    @http.route(
        "/work/<string:slug_value>",
        type="http",
        auth="public",
        website=True,
        sitemap=True,
        methods=["GET"],
    )
    def work_detail(self, slug_value, **kwargs):
        work = request.env["monynha.content.query"].get_work_by_slug(
            request.website,
            slug_value,
        )
        if not work:
            raise NotFound()
        return request.render(
            "monynha_content.work_detail",
            {
                "work": work,
                "main_object": work,
            },
        )
