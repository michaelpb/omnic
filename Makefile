.PHONY: help clean clean-pyc clean-build clean-coverage list test test-all coverage docs release sdist js js-watch

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "bump-and-push - run tests, lint, bump patch, push to git, and release on pypi"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "sdist - package"
	@echo "cleanup-pep8 - automatical clean up some linting violations"

clean: clean-build clean-pyc clean-coverage

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

clean-coverage:
	rm -fr docs/htmlcov/

js:
	./bin/omnic --verbose precache-named viewers --type=min.js --force

js-watch:
	find omnic/ -name \*.js | entr -r ./bin/omnic --verbose precache-named viewers --type=min.js  --force

lint:
	# flake8 omnic test # for now ignore linting issues in test
	flake8 omnic

test:
	py.test

test-all:
	tox

test-watch-s:
	find omnic/ test/ -name \*.py | entr -r py.test -s

runserver-watch:
	find omnic/ test/ -name \*.py | entr -r python ./bin/omnic runserver

cleanup-pep8:
	autoflake --in-place --remove-all-unused-imports --remove-unused-variables -r omnic
	autoflake --in-place --remove-all-unused-imports --remove-unused-variables -r test
	autopep8 --in-place -r omnic
	autopep8 --in-place -r test
	isort -rc --atomic omnic
	isort -rc --atomic test

bump-and-push: test lint
	bumpversion patch
	git push
	git push --tags
	make release

coverage:
	coverage run --source omnic `which py.test`
	#coverage run `which py.test`
	coverage report -m
	coverage html -d ./docs/htmlcov/
	xdg-open ./docs/htmlcov/index.html

docs:
	rm -f docs/omnic.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ omnic
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	xdfg-open docs/_build/html/index.html

release: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload

sdist: clean
	python setup.py sdist
	python setup.py bdist_wheel upload
	ls -l dist
