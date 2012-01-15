all: bin/pcreate bin/pserve lib/python*/site-packages/vboxpanel.egg-link bin/nosetests

run: bin/pserve lib/python*/site-packages/vboxpanel.egg-link
	bin/pserve development.ini

test: bin/nosetests
	bin/nosetests

clean:
	find -name '*.pyc' -delete

dist: bin/python
	bin/python setup.py sdist

distclean: clean
	rm -rf bin/ dist/ include/ lib/ vboxpanel.egg-info/ build/
	rm -f local .coverage

lib/python*/site-packages/vboxpanel.egg-link: bin/python setup.py
	bin/python setup.py develop

bin/pcreate bin/pserve: bin/pip
	bin/pip install pyramid

bin/nosetests: bin/pip
	bin/pip install nose

bin/python bin/pip:
	virtualenv --no-site-packages .
