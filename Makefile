.PHONY: clean data lint requirements

#################################################################################
# GLOBALS                                                                       #
#################################################################################

FIG_SIZE := 0.29

RAW := data/raw
PROCESSED := data/processed
INTERIM := data/interim
IMGS := imgs/plots
SENSORS := src/sensors/sensors.yaml
SETTINGS := settings

DATA := $(shell find $(RAW)/ -name '*.log')
YAML := $(shell find $(SETTINGS)/ -name '*.yaml')
INTERIM_SETTINGS := $(addprefix $(INTERIM)/,$(notdir $(patsubst %.yaml,%.json,$(YAML))))
INTERIM_DATA := $(shell find $(INTERIM)/ -name '*.csv')
PLOT_DATA := $(patsubst $(INTERIM)/%.csv,$(IMGS)/%-plot.png,$(INTERIM_DATA))
HIST_PLOT := $(patsubst $(INTERIM)/%.csv,$(IMGS)/%-hist.png,$(INTERIM_DATA))
HIST_STATS := $(patsubst $(INTERIM)/%.csv,$(PROCESSED)/%-stats.tex,$(INTERIM_DATA))
HIST_MAT := $(patsubst $(INTERIM)/%.json,$(IMGS)/%-hist-mat.png,$(INTERIM_SETTINGS))

PROCESS_SCRIPT := src/data/process.py
CALIBRATION_SCRIPT := src/data/calibration.py
PLOT_SCRIPT := src/visualisation/plot.py
HIST_SCRIPT := src/visualisation/hist.py
HIST_MAT_SCRIPT := src/visualisation/hist_matrix.py

FIGURES := $(shell find $(IMGS)/ -name '*.pgf')

# Tikz
TIKZ := $(shell find $(IMGS)/ -name '*.tikz')
TIKZPDF = $(patsubst %.tikz,%.pdf,$(TIKZ))

#################################################################################
# COMMANDS                                                                      #
#################################################################################

requirements:
	pip install -q -r requirements.txt

docs: requirements

data: $(INTERIM_SETTINGS)

calibrate: $(INTERIM_SETTINGS)

plot: $(PLOT_DATA)

hist: $(HIST_PLOT) $(HIST_STATS)

histmat: $(HIST_MAT)

figures: $(TIKZPDF)

cleandata:
	rm -rf $(INTERIM)/*

clean: cleandata
	find . -name "*.pyc" -exec rm {} \;

lint:
	flake8 --exclude=lib/,bin/,docs/conf.py .

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################

$(INTERIM)/%.json: $(SETTINGS)/%.yaml $(SENSORS) $(DATA) $(PROCESS_SCRIPT)
	python $(PROCESS_SCRIPT) $< $(SENSORS) $(RAW) -o $@

$(INTERIM)/%.json: $(INTERIM)/%.json $(DATA) $(CALIBRATION_SCRIPT)
	python $(CALIBRATION_SCRIPT) $< -o $@ 

$(IMGS)/%-plot.png: $(INTERIM)/%.csv $(PLOT_SCRIPT)
	python $(PLOT_SCRIPT) $< -o $@ -f $(FIG_SIZE)

$(IMGS)/%-hist.png $(PROCESSED)/%-hist.csv: $(INTERIM)/%.csv $(HIST_SCRIPT)
	python $(HIST_SCRIPT) $< -p $(IMGS)/$*-hist.png -s $(PROCESSED)/$*-hist.csv -f $(FIG_SIZE)

$(IMGS)/%-hist-mat.png: $(INTERIM)/%.json $(DATA) $(HIST_MAT_SCRIPT)
	python $(HIST_MAT_SCRIPT) $< -o $@ -f 0.99

# Generate PDF from TIKZ
%.pdf: %.tikz $(FIGURES)
	FILE=$(notdir $<)
	cd $(dir $<); \
	pdflatex $(notdir $<); \
	rm -f *.aux *.end *.fls *.log *.out *.fdb_latexmk
	@echo $<

# generate PDF
%.pdf: %.tex
	FILE=$(notdir $*)
	cd $(dir $*); \
	latexmk -pdf -pv -pdflatex="pdflatex --shell-escape -halt-on-error %O %S" $(notdir $*); \
	rm -f *.aux *.end *.fls *.log *.out *.fdb_latexmk *.bbl *.bcf *.blg *-blx.aux *-blx.bib *.brf *.run.xml
	@echo $*
