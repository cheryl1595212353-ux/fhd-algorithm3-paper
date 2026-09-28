.PHONY: pdf experiments figures application-figures preview

PYTHON ?= python3

pdf:
	latexmk -norc -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex

experiments:
	latexmk -norc -pdf -interaction=nonstopmode -halt-on-error -outdir=build experiments.tex

figures:
	$(PYTHON) scripts/plot_convergence.py
	$(PYTHON) scripts/plot_energy.py

application-figures:
	$(PYTHON) scripts/plot_applications.py $(if $(TEX_ENGINE),--engine $(TEX_ENGINE),)

preview: pdf experiments
	cp build/main.pdf previews/manuscript.pdf
	cp build/experiments.pdf previews/numerical_experiments.pdf
