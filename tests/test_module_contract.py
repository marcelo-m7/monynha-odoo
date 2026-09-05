import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _manifest(addon):
    return ast.literal_eval((ROOT / addon / '__manifest__.py').read_text())


def test_two_addons_exist_with_expected_manifests():
    theme = ROOT / 'theme_monynha' / '__manifest__.py'
    lead = ROOT / 'monynha_lead_generator' / '__manifest__.py'
    assert theme.exists()
    assert lead.exists()
    theme_manifest = _manifest('theme_monynha')
    lead_manifest = _manifest('monynha_lead_generator')
    assert 'theme_common' in theme_manifest['depends']
    assert 'monynha_lead_generator' not in theme_manifest['depends']
    assert 'crm' in lead_manifest['depends']
    assert 'website' in lead_manifest['depends']
    assert 'theme_monynha' not in lead_manifest['depends']


def test_theme_registers_monynha_snippet_group_and_m2_snippets():
    core = (ROOT / 'theme_monynha' / 'views' / 'snippets.xml').read_text()
    m2_path = ROOT / 'theme_monynha' / 'views' / 'snippets_m2.xml'
    assert 'snippet-group="monynha"' in core
    assert m2_path.exists()
    m2 = m2_path.read_text()
    for snippet in (
        's_monynha_signal',
        's_monynha_selected_work',
        's_monynha_capability',
        's_monynha_manifesto',
        's_monynha_metrics',
        's_monynha_faq',
        's_monynha_intro',
    ):
        assert snippet in m2


def test_theme_loads_tokens_before_components_and_keeps_reduced_motion():
    manifest = _manifest('theme_monynha')
    assets = manifest['assets']['web.assets_frontend']
    tokens = 'theme_monynha/static/src/scss/tokens.scss'
    components = 'theme_monynha/static/src/scss/components.scss'
    assert tokens in assets
    assert assets.index(tokens) < assets.index(components)
    scss = '\n'.join(
        path.read_text()
        for path in (ROOT / 'theme_monynha' / 'static' / 'src' / 'scss').glob('*.scss')
    )
    assert 'prefers-reduced-motion' in scss


def test_theme_uses_odoo_native_page_and_menu_templates():
    pages_path = ROOT / 'theme_monynha' / 'data' / 'pages.xml'
    menu_path = ROOT / 'theme_monynha' / 'data' / 'menu.xml'
    assert pages_path.exists()
    assert menu_path.exists()
    pages = pages_path.read_text()
    menu = menu_path.read_text()
    assert 'model="theme.website.page"' in pages
    assert 'model="website.page"' not in pages
    assert 'model="theme.website.menu"' in menu
    assert 'model="website.menu"' not in menu
    assert '<field name="url">/start</field>' in pages
    manifest = _manifest('theme_monynha')
    homepage = manifest.get('configurator_snippets', {}).get('homepage', [])
    assert 's_monynha_hero' in homepage
    assert 's_monynha_cta' in homepage


def test_lead_generator_uses_crm_lead_and_secure_public_report_token():
    lead_model = (ROOT / 'monynha_lead_generator' / 'models' / 'crm_lead.py').read_text()
    diagnosis_model = (ROOT / 'monynha_lead_generator' / 'models' / 'diagnosis.py').read_text()
    controller = (ROOT / 'monynha_lead_generator' / 'controllers' / 'main.py').read_text()
    assert '_inherit = "crm.lead"' in lead_model
    assert '_name = "monynha.lead.diagnosis"' in diagnosis_model
    assert 'secrets.token_urlsafe' in diagnosis_model
    assert '/diagnosis/<string:token>' in controller
    assert 'ALLOWED_SUBMISSION_FIELDS' in controller
    assert '/monynha/diagnosis/followup' in controller


def test_diagnosis_access_rules_follow_standard_crm_visibility():
    security_path = ROOT / 'monynha_lead_generator' / 'security' / 'monynha_security.xml'
    assert security_path.exists()
    security = security_path.read_text()
    assert "('lead_id.user_id','=',user.id)" in security
    assert "('lead_id.user_id','=',False)" in security
    assert 'sales_team.group_sale_salesman_all_leads' in security
    assert "('lead_id.company_id', 'in', company_ids + [False])" in security
    assert 'security/monynha_security.xml' in _manifest('monynha_lead_generator')['data']


def test_discovery_keeps_progressive_accessible_keyboard_and_draft_behavior():
    js = (ROOT / 'monynha_lead_generator' / 'static' / 'src' / 'js' / 'discovery.js').read_text()
    templates = (ROOT / 'monynha_lead_generator' / 'views' / 'templates.xml').read_text()
    assert 'monynha_discovery_draft_v1' in js
    assert 'event.key === "Escape"' in js
    assert 'event.key === "Enter"' in js
    assert 'submitButton.disabled = true' in js
    assert 'submitButton.disabled = false' in js
    assert 'matchMedia("(pointer: coarse)")' in js
    assert 'role="progressbar"' in templates
    assert 'data-monynha-progress-text' in templates
    assert 'aria-live="polite"' in templates
    assert 'react' not in js.lower()
    assert 'vue' not in js.lower()


def test_discovery_draft_storage_is_optional_to_the_submission_flow():
    js = (ROOT / 'monynha_lead_generator' / 'static' / 'src' / 'js' / 'discovery.js').read_text()
    assert 'function saveDraft(' in js
    assert 'function clearDraft(' in js
    assert 'saveDraft(state)' in js
    assert 'clearDraft()' in js


def test_followup_idempotency_is_serialized_at_the_crm_lead_row():
    diagnosis = (ROOT / 'monynha_lead_generator' / 'models' / 'diagnosis.py').read_text()
    assert 'FOR UPDATE' in diagnosis
    assert 'invalidate_recordset(["monynha_followup_requested_at"])' in diagnosis


def test_project_signal_followup_keeps_contact_fallback_on_rpc_failure():
    report_js = (ROOT / 'monynha_lead_generator' / 'static' / 'src' / 'js' / 'report.js').read_text()
    assert 'window.location.assign(link.href)' in report_js


def test_odoo19_constraint_api_and_scss_compatibility():
    diagnosis = (ROOT / 'monynha_lead_generator' / 'models' / 'diagnosis.py').read_text()
    scss = (ROOT / 'monynha_lead_generator' / 'static' / 'src' / 'scss' / 'lead_generator.scss').read_text()
    assert '_sql_constraints' not in diagnosis
    assert 'models.Constraint(' in diagnosis
    assert 'width: min(' not in scss
