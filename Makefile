# ---- config ----
TEMPLATE := default.html
OUTDIR   := .
STATUSES ?= 400 401 403 504

# Derived targets (no leading ./ in names)
PAGES := $(addsuffix .html,$(STATUSES))

.PHONY: all clean list serve pages
all: $(PAGES)

# Don’t try to (re)build the template from itself
$(TEMPLATE): ;

# Build only the pages we want (static pattern rule)
$(PAGES): %.html: $(TEMPLATE)
	@status="$*"; \
	echo "Generating $@ from $(TEMPLATE) (STATUS=$$status)"; \
	sed -e "s/~STATUS~/$$status/g" "$<" > "$@"

# build a single page: `make 502`
$(filter-out all clean list serve pages,$(MAKECMDGOALS)):
	@$(MAKE) $@.html

clean:
	@rm -f $(PAGES)

list:
	@printf "%s\n" $(PAGES)

serve: all
	@python3 -m http.server 8080

pages: all