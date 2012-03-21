all: bin/pcreate bin/pserve lib/python*/site-packages/vboxpanel.egg-link bin/nosetests

run: bin/pserve lib/python*/site-packages/vboxpanel.egg-link
	bin/pserve development.ini --reload

test: bin/nosetests
	bin/nosetests

update-all-packages: bin/pip
	bin/pip install -U nose pyramid pyramid_debugtoolbar waitress
	make

update-requirements: bin/pip
	PYTHONPATH= bin/pip freeze | grep -v vboxpanel > requirements.txt

update:
	git pull
	make
	touch pyramid.wsgi

clean:
	find -name '*.pyc' -delete

dist: bin/python
	bin/python setup.py sdist

distclean: clean
	rm -rf bin/ dist/ include/ lib/ vboxpanel.egg-info/ build/
	rm -f local .coverage tags

lib/python*/site-packages/vboxpanel.egg-link: bin/python setup.py
	bin/python setup.py develop

bin/pcreate bin/pserve: bin/pip
	bin/pip install pyramid

bin/nosetests: bin/pip
	bin/pip install nose

bin/python bin/pip:
	virtualenv --no-site-packages .
