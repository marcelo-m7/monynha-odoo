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
    assert set(first) == {'overall', 'digital_maturity', 'automation_potential', 'process_clarity', 'odoo_fit', 'signals'}
    for key in ('overall', 'digital_maturity', 'automation_potential', 'process_clarity', 'odoo_fit'):
        assert 0 <= first[key] <= 100
    assert isinstance(first['signals'], list)


def test_manual_service_business_has_high_automation_signal():
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
