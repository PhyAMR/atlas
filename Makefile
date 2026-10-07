BIN ?= $(HOME)/.local/bin
SOLITUDE ?= $(HOME)/.config/omarchy/themes/atlas-solitude
INK ?= $(HOME)/.config/omarchy/themes/atlas-ink

.PHONY: install uninstall wallpapers

# Put the birds screensaver on PATH as `atlas-screensaver` (a link, so edits here apply).
install:
	mkdir -p $(BIN)
	chmod +x screensaver/launch build-wallpapers.sh
	ln -sfn $(CURDIR)/screensaver/launch $(BIN)/atlas-screensaver
	@echo "Installed $(BIN)/atlas-screensaver"

uninstall:
	rm -f $(BIN)/atlas-screensaver

# Re-render every plate into both themes: make wallpapers [SOLITUDE=dir] [INK=dir]
wallpapers:
	./build-wallpapers.sh "$(SOLITUDE)" "$(INK)"
