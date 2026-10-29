.PHONY: all serve

# Regenerate every page from template.html (see build.py)
all:
	@python3 build.py

serve: all
	@python3 -m http.server 8080
