# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = ForemanAnsibleModules
SOURCEDIR     = .
BUILDDIR      = _build

ANSIBLEGIT    = .tmp/ansible

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile generate-docs

$(ANSIBLEGIT):
	git clone --depth=1 http://github.com/ansible/ansible $(ANSIBLEGIT)

generate-docs: $(ANSIBLEGIT)
	rm -rf ./modules/
	source $(ANSIBLEGIT)/hacking/env-setup && python $(ANSIBLEGIT)/docs/bin/plugin_formatter.py --module-dir ../modules --template-dir ./_templates --template-dir $(ANSIBLEGIT)/docs/templates --type rst --output-dir ./modules/

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile generate-docs
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
