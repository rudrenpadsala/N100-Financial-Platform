# ==========================================
# N100 Financial Intelligence Platform
# Makefile
# ==========================================

load:
	python src/etl/load_database.py

validate:
	python src/etl/validator.py

test:
	python -m pytest -v

report:
	python src/etl/review_summary.py

dashboard:
	streamlit run src/dashboard/app.py

api:
	uvicorn src.api.main:app --reload

ratios:
	python src/analytics/kpi_engine.py

clean:
	@echo Cleaning output folder...