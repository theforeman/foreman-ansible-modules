NAMESPACE := $(shell python -c 'import yaml; print(yaml.safe_load(open("galaxy.yml"))["namespace"])')
NAME := $(shell python -c 'import yaml; print(yaml.safe_load(open("galaxy.yml"))["name"])')
VERSION := $(shell python -c 'import yaml; print(yaml.safe_load(open("galaxy.yml"))["version"])')
MANIFEST := build/collections/ansible_collections/$(NAMESPACE)/$(NAME)/MANIFEST.json

PLUGIN_TYPES := $(filter-out __%,$(notdir $(wildcard plugins/*)))
METADATA := galaxy.yml LICENSE README.md
$(foreach PLUGIN_TYPE,$(PLUGIN_TYPES),$(eval _$(PLUGIN_TYPE) := $(filter-out %__init__.py,$(wildcard plugins/$(PLUGIN_TYPE)/*.py))))
DEPENDENCIES := $(METADATA) $(foreach PLUGIN_TYPE,$(PLUGIN_TYPES),$(_$(PLUGIN_TYPE)))

PYTHON_VERSION = 3.7
SANITY_OPTS = --venv
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
	@echo "Building collection $(NAMESPACE)-$(NAME)-$(VERSION)"
	@echo $(foreach PLUGIN_TYPE,$(PLUGIN_TYPES),"\n  $(PLUGIN_TYPE): $(basename $(notdir $(_$(PLUGIN_TYPE))))")

lint: $(MANIFEST) | tests/test_playbooks/vars/server.yml
	yamllint -f parsable tests/test_playbooks
	ansible-playbook --syntax-check tests/test_playbooks/*.yml | grep -v '^$$'
	flake8 --ignore=E402,W503 --max-line-length=160 plugins/ tests/

sanity: $(MANIFEST)
	# Fake a fresh git repo for ansible-test
	cd $(<D) ; git init ; echo tests > .gitignore ; ansible-test sanity $(SANITY_OPTS) --python $(PYTHON_VERSION)

test: | tests/test_playbooks/vars/server.yml
	$(PYTEST) $(TEST)

test-crud: | tests/test_playbooks/vars/server.yml
	$(PYTEST) 'tests/test_crud.py::test_crud'

test-check-mode: | tests/test_playbooks/vars/server.yml
	$(PYTEST) 'tests/test_crud.py::test_check_mode'

test-other:
	$(PYTEST) -k 'not test_crud.py'

test_%: FORCE | tests/test_playbooks/vars/server.yml
	pytest -v 'tests/test_crud.py::test_crud[$*]' 'tests/test_crud.py::test_check_mode[$*]'

record_%: FORCE
	$(RM) tests/test_playbooks/fixtures/$*-*.yml
	pytest -v 'tests/test_crud.py::test_crud[$*]' --record

clean_%: FORCE
	ansible-playbook --tags teardown,cleanup -i tests/inventory/hosts 'tests/test_playbooks/$*.yml'

setup: test-setup

test-setup: | tests/test_playbooks/vars/server.yml
	pip install --upgrade 'pip<20'
	pip install -r requirements-dev.txt

tests/test_playbooks/vars/server.yml:
	cp $@.example $@
	@echo "For recording, please adjust $@ to match your reference server."

dist-test: $(MANIFEST)
	ANSIBLE_COLLECTIONS_PATHS=build/collections ansible -m theforeman.foreman.foreman_organization -a "username=admin password=changeme server_url=https://foreman.example.test name=collectiontest" localhost | grep -q "Failed to connect to Foreman server"
	ANSIBLE_COLLECTIONS_PATHS=build/collections ansible-doc theforeman.foreman.foreman_organization | grep -q "Manage Foreman Organization"

$(MANIFEST): $(NAMESPACE)-$(NAME)-$(VERSION).tar.gz
	ansible-galaxy collection install -p build/collections $< --force

# fix the imports to use the collection namespace
build/src/plugins/modules/%.py: plugins/modules/%.py | build
	sed -e '/ansible.module_utils.foreman_helper/ s/ansible.module_utils/ansible_collections.theforeman.foreman.plugins.module_utils/g' \
	-e '/extends_documentation_fragment/{:1 n; s/- foreman/- theforeman.foreman.foreman/; t1}' $< > $@

# adjust README.md not to point to files that we don't ship in the collection
build/src/README.md: README.md | build
	sed -e '/Documentation how to/d' $< > $@

build/src/%: % | build
	cp $< $@

build:
	-mkdir build build/src build/src/plugins $(addprefix build/src/plugins/,$(PLUGIN_TYPES))

$(NAMESPACE)-$(NAME)-$(VERSION).tar.gz: $(addprefix build/src/,$(DEPENDENCIES)) | build
	ansible-galaxy collection build build/src --force

dist: $(NAMESPACE)-$(NAME)-$(VERSION).tar.gz

clean:
	rm -rf build

doc-setup:
	pip install -r docs/requirements.txt
doc:
	make -C docs html

FORCE:

.PHONY: help dist lint sanity test test-crud test-check-mode test-other setup test-setup FORCE
