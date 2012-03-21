pypackage = vboxpanel
egg_link = lib/python*/site-packages/$(pypackage).egg-link

all: bin/pcreate bin/pserve $(egg_link) bin/nosetests

run: bin/pserve $(egg_link)
	bin/pserve development.ini --reload

test: bin/nosetests
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

$(egg_link): bin/python setup.py
	bin/python setup.py develop

bin/pcreate bin/pserve: bin/pip
	bin/pip install pyramid

bin/nosetests: bin/pip
	bin/pip install nose

bin/python bin/pip:
	virtualenv --no-site-packages .
