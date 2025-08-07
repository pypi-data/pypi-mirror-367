SERVICE_PACKAGE = oops
ENV = $(CURDIR)/env
PIP = $(ENV)/bin/pip
TMPDIR = $(CURDIR)/tmp

DEPENDENCY_REPO ?= https://git.launchpad.net/~launchpad/python-oops/+git/dependencies
DEPENDENCY_DIR ?= $(TMPDIR)/dependencies

$(ENV)/.created: | update-dependencies
	python3 -m venv $(ENV)
	ln -sfn env/bin bin
	$(PIP) install -f file://$(DEPENDENCY_DIR) --no-index pip==25.0.1
	$(PIP) install -f file://$(DEPENDENCY_DIR) --no-index \
		wheel==0.45.1 setuptools==75.3.2
	$(PIP) install -f file://$(DEPENDENCY_DIR) --no-index \
		-r requirements.txt -e .
	@touch $@

$(DEPENDENCY_DIR):
	git clone $(DEPENDENCY_REPO) $(DEPENDENCY_DIR)

update-dependencies: $(DEPENDENCY_DIR)
	cd $(DEPENDENCY_DIR) && git pull $(DEPENDENCY_REPO)

bootstrap build: $(ENV)/.created

check:
	tox

clean:
	rm -rf $(ENV) .tox
	rm -rf $(TMPDIR)
	rm -f bin
	find -name '__pycache__' -print0 | xargs -0 rm -rf
	find -name '*.~*' -delete

.PHONY: update-dependencies check clean
