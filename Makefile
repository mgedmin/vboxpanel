PYTHON = python

pypackage = vboxpanel
py_ver = $(shell $(PYTHON) -c 'import sys; sys.stdout.write(sys.version[:3])')
egg_link = lib/python$(py_ver)/site-packages/$(pypackage).egg-link

all: $(egg_link) bin/pcreate bin/pserve bin/nosetests bin/coverage

run: bin/pserve $(egg_link)
	bin/pserve development.ini --reload

test: bin/nosetests bin/coverage
	bin/nosetests

update-all-packages: bin/pip
	bin/pip install -U nose pyramid pyramid_debugtoolbar waitress
	make
	make update-requirements

update-requirements: bin/pip
	PYTHONPATH= bin/pip freeze | grep -v '^-e .*$(pypackage)-dev$$' > requirements.txt

update:
	git pull
	make
	touch pyramid.wsgi

clean:
	find -name '*.pyc' -delete

dist: bin/python
	bin/python setup.py sdist

distclean: clean
	rm -rf bin/ dist/ include/ lib/ *.egg-info/ build/
	rm -f local .coverage tags

$(egg_link): bin/pip setup.py
	bin/pip install -e .

bin/pcreate bin/pserve: bin/pip
	bin/pip install pyramid

bin/nosetests: bin/pip
	bin/pip install nose

bin/coverage: bin/pip
	bin/pip install coverage

bin/python bin/pip:
	virtualenv -p $(PYTHON) --no-site-packages .
