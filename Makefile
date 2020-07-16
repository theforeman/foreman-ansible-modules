NAMESPACE := $(shell python -c 'import yaml; print(yaml.safe_load(open("galaxy.yml"))["namespace"])')
NAME := $(shell python -c 'import yaml; print(yaml.safe_load(open("galaxy.yml"))["name"])')
VERSION := $(shell python -c 'import yaml; print(yaml.safe_load(open("galaxy.yml"))["version"])')
MANIFEST := build/collections/ansible_collections/$(NAMESPACE)/$(NAME)/MANIFEST.json

PLUGIN_TYPES := $(filter-out __%,$(notdir $(wildcard plugins/*)))
METADATA := galaxy.yml LICENSE README.md meta/runtime.yml requirements.txt requirements-common.txt
$(foreach PLUGIN_TYPE,$(PLUGIN_TYPES),$(eval _$(PLUGIN_TYPE) := $(filter-out %__init__.py,$(wildcard plugins/$(PLUGIN_TYPE)/*.py))))
DEPENDENCIES := $(METADATA) $(foreach PLUGIN_TYPE,$(PLUGIN_TYPES),$(_$(PLUGIN_TYPE)))

PYTHON_VERSION = 3.7
COLLECTION_COMMAND ?= ansible-galaxy
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

test: $(MANIFEST) | tests/test_playbooks/vars/server.yml
	$(PYTEST) $(TEST)

test-crud: $(MANIFEST) | tests/test_playbooks/vars/server.yml
	$(PYTEST) 'tests/test_crud.py::test_crud'

test-check-mode: $(MANIFEST) | tests/test_playbooks/vars/server.yml
	$(PYTEST) 'tests/test_crud.py::test_check_mode'

test-other:
	$(PYTEST) -k 'not test_crud.py'

test_%: FORCE $(MANIFEST) | tests/test_playbooks/vars/server.yml
	pytest -v 'tests/test_crud.py::test_crud[$*]' 'tests/test_crud.py::test_check_mode[$*]'

record_%: FORCE $(MANIFEST)
	$(RM) tests/test_playbooks/fixtures/$*-*.yml
	pytest -v 'tests/test_crud.py::test_crud[$*]' --record

clean_%: FORCE $(MANIFEST)
	ansible-playbook --tags teardown,cleanup -i tests/inventory/hosts 'tests/test_playbooks/$*.yml'

setup: test-setup

test-setup: | tests/test_playbooks/vars/server.yml
	pip install --upgrade 'pip<20'
	pip install -r requirements-dev.txt

tests/test_playbooks/vars/server.yml:
	cp $@.example $@
	@echo "For recording, please adjust $@ to match your reference server."

dist-test: $(MANIFEST)
	ANSIBLE_COLLECTIONS_PATHS=build/collections ansible -m $(NAMESPACE).$(NAME).organization -a "username=admin password=changeme server_url=https://foreman.example.test name=collectiontest" localhost | grep -q "Failed to connect to Foreman server"
	ANSIBLE_COLLECTIONS_PATHS=build/collections ansible-doc $(NAMESPACE).$(NAME).organization | grep -q "Manage Organization"

$(MANIFEST): $(NAMESPACE)-$(NAME)-$(VERSION).tar.gz
ifeq ($(COLLECTION_COMMAND),mazer)
	# No idea, why this fails. But mazer is old and deprecated so unlikely to beeing fixed...
	# mazer install --collections-path build/collections $<
	-mkdir build/collections build/collections/ansible_collections build/collections/ansible_collections/$(NAMESPACE) build/collections/ansible_collections/$(NAMESPACE)/$(NAME)
	tar xf $< -C build/collections/ansible_collections/$(NAMESPACE)/$(NAME)
else
	ansible-galaxy collection install -p build/collections $< --force
endif

build/src/%: % | build/src
	cp $< $@

build/src:
	-mkdir -p build build/src build/src/meta build/src/plugins $(addprefix build/src/plugins/,$(PLUGIN_TYPES))

$(NAMESPACE)-$(NAME)-$(VERSION).tar.gz: $(addprefix build/src/,$(DEPENDENCIES)) | build/src
ifeq ($(COLLECTION_COMMAND),mazer)
	mazer build --collection-path=build/src
	cp build/src/releases/$@ .
else
	ansible-galaxy collection build build/src --force
endif

dist: $(NAMESPACE)-$(NAME)-$(VERSION).tar.gz

clean:
	rm -rf build

doc-setup:
	pip install -r docs/requirements.txt
doc: $(MANIFEST)
	make -C docs html

FORCE:

.PHONY: help dist lint sanity test test-crud test-check-mode test-other setup test-setup FORCE
