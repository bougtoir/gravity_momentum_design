PY ?= python3
all: test analysis figures stats manuscript submission
test:
	$(PY) -m pytest tests/ -q
analysis:
	$(PY) scripts/run_analysis.py --mc 2000
figures:
	$(PY) scripts/make_figures.py
stats:
	$(PY) scripts/make_stats.py
manuscript:
	$(PY) scripts/make_manuscript.py
submission:
	$(PY) scripts/make_submission.py
