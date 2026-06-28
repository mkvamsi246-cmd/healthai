# HealthInsight AI — Backend Implementation Plan

## Files to Create (~44 files)

### Root
- requirements.txt, .env.example, alembic.ini, README.md

### app/
- __init__.py, main.py, config.py, database.py, dependencies.py

### app/models/
- __init__.py, user.py, report.py, medical_values.py, prediction.py, comparison.py

### app/schemas/
- __init__.py, user.py, report.py, medical_values.py, prediction.py, comparison.py

### app/routers/
- __init__.py, auth.py, reports.py, dashboard.py, health.py

### app/services/
- __init__.py, auth_service.py, ocr_service.py, extraction_service.py,
  ml_service.py, report_service.py, comparison_service.py, pdf_service.py

### app/utils/
- __init__.py, jwt_utils.py, file_utils.py, medical_utils.py, response_utils.py

### app/knowledge/
- medical_reference.json

### ml/
- __init__.py, predict.py

### alembic/
- env.py, script.py.mako
