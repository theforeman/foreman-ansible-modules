TEST=
DATA=$(shell echo $(MODULE) | sed 's/\(foreman\|katello\)_//; s/_/-/g')
PDB_PATH=$(shell find /usr/lib{,64} -type f -executable -name pdb.py 2> /dev/null)
ifeq ($(PDB_PATH),)
	PDB_PATH=$(shell which pdb)
endif
MODULE_PATH=plugins/modules/$(MODULE).py
DEBUG_DATA_PATH=tests/debug_data/$(DATA).json
DEBUG_OPTIONS=-m $(MODULE_PATH) -a @$(DEBUG_DATA_PATH) -D $(PDB_PATH)

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
	pycodestyle --ignore=E402,E722 --max-line-length=160 plugins/modules plugins/module_utils tests/

test:
	pytest -v $(TEST)

test_%: FORCE
	pytest 'tests/test_crud.py::test_crud[$*]'

record_%: FORCE
	$(RM) tests/test_playbooks/fixtures/$*-*.yml
	pytest 'tests/test_crud.py::test_crud[$*]' --record

clean_%: FORCE
	ansible-playbook --tags teardown,cleanup -i tests/inventory/hosts 'tests/test_playbooks/$*.yml'

sanity:
	ansible-playbook tests/extras/sanity.yml

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
	mazer build

doc-setup:
	pip install -r docs/requirements.txt
doc:
	make -C docs html

FORCE:

.PHONY: help debug lint test setup debug-setup test-setup FORCE
