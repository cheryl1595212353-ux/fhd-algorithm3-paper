.PHONY: check tables figures pdf preview experiments energy-figures legacy-energy-figures application-figures

PYTHON ?= python3
TEX_ENGINE ?= auto

check:
	$(PYTHON) scripts/validate.py

tables:
	$(PYTHON) scripts/generate_tables.py

figures:
	$(PYTHON) scripts/plot_convergence.py

pdf: check
	$(PYTHON) scripts/build_pdf.py --engine "$(TEX_ENGINE)"

preview: pdf
	$(PYTHON) scripts/export_previews.py

experiments: preview

energy-figures:
	$(PYTHON) scripts/plot_energy_high_order.py

legacy-energy-figures:
	$(PYTHON) scripts/plot_energy.py

application-figures:
	$(PYTHON) scripts/plot_applications.py $(if $(filter-out auto,$(TEX_ENGINE)),--engine "$(TEX_ENGINE)",)
