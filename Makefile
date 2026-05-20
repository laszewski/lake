.PHONY: pdf

pdf: clean cover render
	open  _book/Observing-Eagles.pdf

all: clean 
	quarto render --to html
	quarto render --to epub
	quarto render --to pdf

html: clean cover
	quarto preview --to html

publish-git:
	/Users/grey/.pyenv/versions/3.14.4/bin/python -m mkdocs gh-deploy

publish: build
	rsync --progress -pavz site/ lake:./lake.vonlaszewski.com

# scp -r public/* user@remote_host:/path/to/CCC/

clean:
	rm -rf _book/
	rm -rf .quarto/
	rm -rf *_cache/
	rm -rf *_files/

view:
	open _book/Observing-Eagles.pdf

epub: clean cover
	quarto render --to epub
	open  _book/Observing-Eagles.epub

cover:
	@echo "Generating book cover from _quarto.yml..."
	rm -f cover.pdf cover.png
	python bin/cover.py

render: cover
	quarto render --to pdf
	# Merge custom cover (images/cover.pdf) with the main book
	qpdf --empty --pages images/cover.pdf _book/Observing-Eagles.pdf -- final_book.pdf
	mv final_book.pdf _book/Observing-Eagles.pdf

serve:
	lsof -ti:8000 | xargs kill -9 || true
	lsof -ti:8787 | xargs kill -9 || true
	npx wrangler dev worker.js --port 8787 &
	sleep 2
	/Users/grey/.pyenv/versions/3.14.4/bin/python -m mkdocs serve --livereload

# To develop locally:
# 1. Run 'make dev-worker' in one terminal
# 2. Run 'make serve' in another terminal
# 3. Note: You may need to update the proxyUrl in .md files to http://localhost:8787/weather for local testing

build:
	/Users/grey/.pyenv/versions/3.14.4/bin/python -m mkdocs build
	

	
