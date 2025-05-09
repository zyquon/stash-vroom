# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= --verbose
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = ../docs

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

clean: Makefile
	rm -rvf $(BUILDDIR) stash_vroom.rst stash_vroom.*.rst

nodoc: Makefile
	rm -rvf $(BUILDDIR) && git checkout HEAD $(BUILDDIR)

stash_vroom.rst: Makefile
	# sphinx-apidoc --force --no-toc --module-first --output-dir $(SOURCEDIR)/ ../stash_vroom
	sphinx-apidoc --force --no-toc --module-first --separate --output-dir $(SOURCEDIR)/ ../stash_vroom

html: Makefile stash_vroom.rst
	$(SPHINXBUILD) -M "html" "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	touch "$(BUILDDIR)/.nojekyll"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)