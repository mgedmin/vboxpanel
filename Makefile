all: bin/pcreate bin/pserve lib/python*/site-packages/vboxpanel.egg-link

run: bin/pserve lib/python*/site-packages/vboxpanel.egg-link
	bin/pserve development.ini

lib/python*/site-packages/vboxpanel.egg-link: bin/python setup.py
	bin/python setup.py develop

bin/pcreate bin/pserve: bin/pip
	bin/pip install pyramid

bin/python bin/pip:
	virtualenv .
