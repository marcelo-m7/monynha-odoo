# Monynha Odoo

Native Odoo 19 Community implementation of the Monynha Softwares website experience and lead-generation workflow.

## Addons

- `theme_monynha`: visual identity and reusable Website Builder snippets inspired by the historical `open2.tech` v6.0.1 lead-generator experience.
- `monynha_lead_generator`: interactive discovery wizard, standard `crm.lead` integration, deterministic diagnosis history, secure public Project Signal, and email notification.

The addons are intentionally independent: neither depends on the other.

## M1 flow

`/start` → discovery wizard → `crm.lead` → `local_rules` diagnosis → `/diagnosis/<secure-token>`.

The lead is created before diagnosis processing. External AI providers are not required for M1.

## Development

Contract tests:

```bash
pytest -q tests
```

GitHub Actions also installs and upgrades both addons against the official Odoo 19 Docker image and PostgreSQL 16.
