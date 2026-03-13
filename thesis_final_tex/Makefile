LATEXMK ?= latexmk
MAIN = main

all: pdf

pdf:
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error $(MAIN).tex

clean:
	$(LATEXMK) -C $(MAIN).tex

.PHONY: all pdf clean