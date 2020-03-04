NAMESPACE := $(shell python -c 'import yaml; print(yaml.safe_load(open("galaxy.yml"))["namespace"])')
NAME := $(shell python -c 'import yaml; print(yaml.safe_load(open("galaxy.yml"))["name"])')
VERSION := $(shell python -c 'import yaml; print(yaml.safe_load(open("galaxy.yml"))["version"])')
MANIFEST := build/collections/ansible_collections/$(NAMESPACE)/$(NAME)/MANIFEST.json

FILTER := $(shell find plugins/filter -name *.py)
MODULES := $(shell find plugins/modules -name *.py)
MODULE_UTILS := $(shell find plugins/module_utils -name *.py)
DOC_FRAGMENTS := $(shell find plugins/doc_fragments -name *.py)

PYTHON_VERSION = 3.7
TEST=
PYTEST=pytest -n 4 --boxed -v

default: help
help:
	@echo "Please use \`make <target>' where <target> is one of:"
	@echo "  help           to show this message"
	@echo "  info           to show infos about the collection"
	@echo "  lint           to run code linting"
	@echo "  test           to run unit tests"
	@echo "  sanity         to run santy tests"
	@echo "  setup          to set up test, lint"
	@echo "  test-setup     to install test dependencies"
	@echo "  test_<test>    to run a specific unittest"
	@echo "  record_<test>  to (re-)record the server answers for a specific test"
	@echo "  clean_<test>   to run a specific test playbook with the teardown and cleanup tags"
	@echo "  dist           to build the collection artifact"

info:
	@echo Building collection $(NAMESPACE)-$(NAME)-$(VERSION)
	@echo   filter: $(FILTER)
	@echo   modules: $(MODULES)
	@echo   module_utils: $(MODULE_UTILS)
	@echo   doc_fragments: $(DOC_FRAGMENTS)

lint: tests/test_playbooks/vars/server.yml $(MANIFEST)
	yamllint -f parsable tests/test_playbooks
	ansible-playbook --syntax-check tests/test_playbooks/*.yml | grep -v '^$$'
	flake8 --ignore=E402,W503 --max-line-length=160 plugins/ tests/

sanity: $(MANIFEST)
	# Fake a fresh git repo for ansible-test
	cd $(<D) ; git init ; echo tests > .gitignore ; ansible-test sanity --local --python $(PYTHON_VERSION)

test:
	$(PYTEST) $(TEST)

test-crud:
	$(PYTEST) 'tests/test_crud.py::test_crud'

test-check-mode:
	$(PYTEST) 'tests/test_crud.py::test_check_mode'

test-other:
	$(PYTEST) -k 'not test_crud.py'

test_%: FORCE
	pytest -v 'tests/test_crud.py::test_crud[$*]' 'tests/test_crud.py::test_check_mode[$*]'

record_%: FORCE
	$(RM) tests/test_playbooks/fixtures/$*-*.yml
	pytest -v 'tests/test_crud.py::test_crud[$*]' --record

clean_%: FORCE
	ansible-playbook --tags teardown,cleanup -i tests/inventory/hosts 'tests/test_playbooks/$*.yml'

setup: test-setup

test-setup: tests/test_playbooks/vars/server.yml
	pip install --upgrade 'pip<20'
	pip install -r requirements-dev.txt

tests/test_playbooks/vars/server.yml:
	cp tests/test_playbooks/vars/server.yml.example tests/test_playbooks/vars/server.yml
	@echo "For recording, please adjust tests/tests_playbooks/vars/server.yml to match your reference server."

dist-test: $(MANIFEST)
	ANSIBLE_COLLECTIONS_PATHS=build/collections ansible -m theforeman.foreman.foreman_organization -a "username=admin password=changeme server_url=https://foreman.example.test name=collectiontest" localhost | grep -q "Failed to connect to Foreman server"
	ANSIBLE_COLLECTIONS_PATHS=build/collections ansible-doc theforeman.foreman.foreman_organization | grep -q "Manage Foreman Organization"

$(MANIFEST): $(NAMESPACE)-$(NAME)-$(VERSION).tar.gz
	ansible-galaxy collection install -p build/collections $+ --force

$(NAMESPACE)-$(NAME)-$(VERSION).tar.gz: galaxy.yml LICENSE README.md $(FILTER) $(MODULES) $(MODULE_UTILS) $(DOC_FRAGMENTS)
	mkdir -p build/src
	cp galaxy.yml LICENSE README.md build/src
	cp -r plugins build/src

	# fix the imports to use the collection namespace
	sed -i '/ansible.module_utils.foreman_helper/ s/ansible.module_utils/ansible_collections.theforeman.foreman.plugins.module_utils/g' build/src/plugins/modules/*.py
	sed -i -e '/extends_documentation_fragment/{:1 n; s/- foreman/- theforeman.foreman.foreman/; t1}' build/src/plugins/modules/*.py

	# adjust README.md not to point to files that we don't ship in the collection
	sed -i '/Documentation how to/d' build/src/README.md

	ansible-galaxy collection build build/src --force

dist: $(NAMESPACE)-$(NAME)-$(VERSION).tar.gz

clean:
	rm -rf build

doc-setup:
	pip install -r docs/requirements.txt
doc:
	make -C docs html

FORCE:

.PHONY: help lint sanity test test-crud test-check-mode test-other setup test-setup FORCE
