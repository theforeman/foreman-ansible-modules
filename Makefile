TEST=
DATA=$(shell echo $(MODULE) | sed 's/\(foreman\|katello\)_//; s/_/-/g')
PDB_PATH=$(shell find /usr/lib{,64} -type f -executable -name pdb.py 2> /dev/null)
ifeq ($(PDB_PATH),)
	PDB_PATH=$(shell which pdb)
endif
MODULE_PATH=plugins/modules/$(MODULE).py
DEBUG_DATA_PATH=tests/debug_data/$(DATA).json
DEBUG_OPTIONS=-m $(MODULE_PATH) -a @$(DEBUG_DATA_PATH) -D $(PDB_PATH)
COLLECTION_TMP:=$(shell mktemp -du)
COLLECTION_INSTALL_TMP:=$(shell mktemp -du)
PYTEST=pytest -n 4 --boxed -v

default: help
help:
	@echo "Please use \`make <target>' where <target> is one of:"
	@echo "  help           to show this message"
	@echo "  lint           to run flake8 and pylint"
	@echo "  test           to run unit tests"
	@echo "  sanity         to run santy tests"
	@echo "  debug          debug a module using the ansible hacking module"
	@echo "  setup          to set up test, lint, and debugging"
	@echo "  test-setup     to install test dependencies"
	@echo "  debug-setup    to set up the ansible hacking module"
	@echo "  test_<test>    to run a specific unittest"
	@echo "  record_<test>  to (re-)record the server answers for a specific test"

lint:
	flake8 --ignore=E402,W503 --max-line-length=160 plugins/ tests/

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

sanity: dist-install
	ansible-playbook $(CURDIR)/tests/extras/sanity.yml -e test_collection_path=$(COLLECTION_INSTALL_TMP)/ansible_collections/theforeman/foreman/

debug:
ifndef MODULE
	$(error MODULE is undefined)
endif
	./.tmp/ansible/hacking/test-module $(DEBUG_OPTIONS)

setup: test-setup debug-setup

debug-setup: .tmp/ansible
.tmp/ansible:
	ansible-playbook debug-setup.yml

test-setup: tests/test_playbooks/vars/server.yml
	pip install --upgrade pip
	pip install -r requirements-dev.txt
	pip install -r https://raw.githubusercontent.com/ansible/ansible/devel/requirements.txt
tests/test_playbooks/vars/server.yml:
	cp tests/test_playbooks/vars/server.yml.example tests/test_playbooks/vars/server.yml

dist:
	mkdir -p $(COLLECTION_TMP)

	# only copy selected files/folders from our git
	git archive HEAD LICENSE README.md galaxy.yml plugins tests/sanity | tar -C $(COLLECTION_TMP) -xf -

	# fix the imports to use the collection namespace
	sed -i '/ansible.module_utils.foreman_helper/ s/ansible.module_utils/ansible_collections.theforeman.foreman.plugins.module_utils/g' $(COLLECTION_TMP)/plugins/modules/*.py
	sed -i -e '/extends_documentation_fragment/{:1 n; s/- foreman/- theforeman.foreman.foreman/; t1}' $(COLLECTION_TMP)/plugins/modules/*.py

	# adjust README.md not to point to files that we don't ship in the collection
	sed -i '/Documentation how to/d' $(COLLECTION_TMP)/README.md

	ansible-galaxy collection build $(COLLECTION_TMP)

	rm -rf $(COLLECTION_TMP)

dist-install: dist
	mkdir -p $(COLLECTION_INSTALL_TMP)

	ansible-galaxy collection install --collections-path $(COLLECTION_INSTALL_TMP) ./theforeman-foreman-*.tar.gz

dist-test: dist-install
	ANSIBLE_COLLECTIONS_PATHS=$(COLLECTION_INSTALL_TMP) ansible -m theforeman.foreman.foreman_organization -a "username=admin password=changeme server_url=https://foreman.example.test name=collectiontest" localhost |grep -q "Failed to connect to Foreman server"
	ANSIBLE_COLLECTIONS_PATHS=$(COLLECTION_INSTALL_TMP) ansible-doc theforeman.foreman.foreman_organization |grep -q "Manage Foreman Organization"

dist-clean:
	rm -rf $(COLLECTION_INSTALL_TMP)

doc-setup:
	pip install -r docs/requirements.txt
doc:
	make -C docs html

FORCE:

.PHONY: help debug lint test test-crud test-check-mode test-other setup debug-setup test-setup FORCE
