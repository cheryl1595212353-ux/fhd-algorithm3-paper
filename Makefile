.PHONY: pdf preview

pdf:
	latexmk -norc -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex

preview: pdf
	cp build/main.pdf previews/manuscript.pdf
