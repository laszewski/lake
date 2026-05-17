.PHONY: pdf

pdf: clean cover render
	open  _book/Observing-Eagles.pdf

all: clean 
	quarto render --to html
	quarto render --to epub
	quarto render --to pdf

html: clean cover
	quarto preview --to html

publish:
	mkdocs gh-deploy

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
	lsof -ti:8000 | xargs kill -9
	mkdocs serve --livereload

build:
	mkdocs build
	

	