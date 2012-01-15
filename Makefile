all: bin/pcreate

bin/pcreate: bin/pip
	bin/pip install pyramid

bin/pip:
	virtualenv .
