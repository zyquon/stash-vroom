# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= --verbose
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build
GH_DOC_DIR    = ../docs

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

nodoc: Makefile
	rm -rvf $(GH_DOC_DIR) && git checkout HEAD $(GH_DOC_DIR)

clean: Makefile nodoc
	rm -rvf $(BUILDDIR) stash_vroom.rst stash_vroom.*.rst

stash_vroom.rst: Makefile
	# sphinx-apidoc --force --no-toc --module-first --output-dir $(SOURCEDIR)/ ../stash_vroom
	sphinx-apidoc --force --no-toc --module-first --separate --output-dir $(SOURCEDIR)/ ../stash_vroom '../stash_vroom/stash_client'

html: Makefile stash_vroom.rst
	$(SPHINXBUILD) -M "html" "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

doc: html
	rm -rf $(GH_DOC_DIR)
	mv -vi $(BUILDDIR)/html $(GH_DOC_DIR)
	touch "$(GH_DOC_DIR)/.nojekyll"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
