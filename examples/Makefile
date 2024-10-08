SOURCES=$(wildcard src/*.py)
TARGETS=$(SOURCES:src/%.py=images/%.svg)

default: $(TARGETS)

images/%.svg: src/%.py
	@mkdir -p images
	python build.py -o $@ $<

clean:
	-rm $(TARGETS)