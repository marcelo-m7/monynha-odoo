from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]


def load_scoring_module():
    path = ROOT / 'monynha_lead_generator' / 'services' / 'scoring.py'
    spec = importlib.util.spec_from_file_location('monynha_scoring', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_scoring_is_deterministic_and_bounded():
    scoring = load_scoring_module()
    answers = {
        'revenue_model': 'service',
        'decision_profile': 'solo',
        'struggle': 'Manual handoffs and duplicated work across sales and operations',
        'website_url': 'https://example.com',
        'instagram_url': '',
        'linkedin_url': '',
    }
    first = scoring.score_discovery(answers)
    second = scoring.score_discovery(dict(answers))
    assert first == second
    assert set(first) == {
        'overall',
        'digital_maturity',
        'automation_potential',
        'process_clarity',
        'odoo_fit',
        'signals',
        'opportunities',
        'recommended_action',
    }
    for key in ('overall', 'digital_maturity', 'automation_potential', 'process_clarity', 'odoo_fit'):
        assert 0 <= first[key] <= 100
    assert isinstance(first['signals'], list)
    assert isinstance(first['opportunities'], list)
    assert first['recommended_action'] in {'clarify', 'automate', 'centralize', 'integrate', 'architecture'}


def test_manual_service_business_has_actionable_automation_signal():
    scoring = load_scoring_module()
    result = scoring.score_discovery({
        'revenue_model': 'service',
        'decision_profile': 'solo',
        'struggle': 'I do everything manually in spreadsheets and repeat the same tasks every day',
        'website_url': '',
        'instagram_url': 'https://instagram.com/example',
        'linkedin_url': '',
    })
    assert result['automation_potential'] >= 70
    assert result['odoo_fit'] >= 60
    assert result['opportunities']
    assert any('automat' in item.lower() for item in result['opportunities'])
    assert result['recommended_action'] == 'automate'


def test_fragmented_systems_prioritize_centralization():
    scoring = load_scoring_module()
    result = scoring.score_discovery({
        'revenue_model': 'service',
        'decision_profile': 'delegate',
        'struggle': 'We have fragmented data across various systems and many tools, with duplicated customer context.',
        'website_url': 'https://example.com',
        'instagram_url': 'https://instagram.com/example',
        'linkedin_url': 'https://linkedin.com/company/example',
    })
    assert any('central' in item.lower() for item in result['opportunities'])
    assert result['recommended_action'] == 'centralize'


def test_unclear_operation_prioritizes_clarity():
    scoring = load_scoring_module()
    result = scoring.score_discovery({
        'revenue_model': 'other',
        'decision_profile': 'unclear',
        'struggle': 'We need to understand ownership, responsibilities and the operating process before building more tools.',
        'website_url': '',
        'instagram_url': '',
        'linkedin_url': '',
    })
    assert result['recommended_action'] == 'clarify'
    assert any('clar' in item.lower() or 'ownership' in item.lower() for item in result['opportunities'])
