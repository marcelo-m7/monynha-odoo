from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_two_addons_exist_with_expected_manifests():
    theme = ROOT / 'theme_monynha' / '__manifest__.py'
    lead = ROOT / 'monynha_lead_generator' / '__manifest__.py'
    assert theme.exists()
    assert lead.exists()
    assert 'theme_common' in theme.read_text()
    lead_text = lead.read_text()
    assert '"crm"' in lead_text or "'crm'" in lead_text
    assert '"website"' in lead_text or "'website'" in lead_text
    assert 'theme_monynha' not in lead_text


def test_theme_registers_monynha_snippet_group_and_core_snippets():
    snippets = (ROOT / 'theme_monynha' / 'views' / 'snippets.xml').read_text()
    assert 'snippet-group="monynha"' in snippets
    for snippet in (
        's_monynha_hero',
        's_monynha_services',
        's_monynha_process',
        's_monynha_labs',
        's_monynha_cta',
    ):
        assert snippet in snippets


def test_lead_generator_uses_crm_lead_and_secure_public_report_token():
    lead_model = (ROOT / 'monynha_lead_generator' / 'models' / 'crm_lead.py').read_text()
    diagnosis_model = (ROOT / 'monynha_lead_generator' / 'models' / 'diagnosis.py').read_text()
    controller = (ROOT / 'monynha_lead_generator' / 'controllers' / 'main.py').read_text()
    assert '_inherit = "crm.lead"' in lead_model
    assert '_name = "monynha.lead.diagnosis"' in diagnosis_model
    assert 'secrets.token_urlsafe' in diagnosis_model
    assert '/diagnosis/<string:token>' in controller
    assert 'ALLOWED_SUBMISSION_FIELDS' in controller


def test_odoo19_constraint_api_and_scss_compatibility():
    diagnosis = (ROOT / 'monynha_lead_generator' / 'models' / 'diagnosis.py').read_text()
    scss = (ROOT / 'monynha_lead_generator' / 'static' / 'src' / 'scss' / 'lead_generator.scss').read_text()
    assert '_sql_constraints' not in diagnosis
    assert 'models.Constraint(' in diagnosis
    assert 'width: min(' not in scss
