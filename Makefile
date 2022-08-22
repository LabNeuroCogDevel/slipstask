.PHONY: res test always
.SUFFIXES:
MAKEFLAGS += --no-builtin-rules

static/js/utils.js: static/js/utils.ts
	tsc -m es2015 --lib esnext,dom -d $<
	tsc -b 

res:  analysis/txt/task.tsv
analysis/txt/res.json: always
	 analysis/fetch.bash > $@

analysis/txt/task.tsv: analysis/txt/res.json
	analysis/json2tsv.bash $<
	# expect output like:
	# nseen   n_of_type participant
	#      1       1 a52a5e65fc3c43f409550dfad1f904f
	#      3       6 a52a5e65fc3c43f409550dfad1f904f
	#     26      12 a52a5e65fc3c43f409550dfad1f904f
	#      1      36 a52a5e65fc3c43f409550dfad1f904f
	git diff analysis/txt/task.tsv|sed -n s/^\+[^+]//p|cut -f1,3|sort |uniq -c|sort -k2,1|cut -f1|uniq -c|sort -k2n

test: tests/.res.tap tests/.pytests
tests/.res.tap: $(wildcard tests/*js)
	# npm test
	jest --json 2>/dev/null | jest-json-to-tap > $@

tests/.pytests: $(wildcard pytest/*.py soapy/*py)
	python -m pytest --tap-stream pytest/ soapy/ --doctest-modules | tee $@

# https://stackoverflow.com/questions/11091623/how-to-install-packages-offline
.ONESHELL:
soapy/wheelhouse.tar.gz: soapy/requirements.txt
	cd soapy
	test ! -d wheelhouse && mkdir wheelhouse
	pip download -r requirements.txt -d wheelhouse
	cp requirements.txt wheelhouse/
	zip -r wheelhouse.zip wheelhouse/
	tar -zcf wheelhouse.tar.gz wheelhouse/
	rm -r wheelhouse

install_depends: soapy/wheelhouse.tar.gz
	# also see run_SOA.bat
	pip install -r wheelhouse/requirements.txt --no-index --find-links wheelhouse
	# copy static/images into soapy/images
	# "C:\Users\foranw\AppData\Local\PsychoPy3\python.exe" -m pip install -r wheelhouse\\requirements.txt --no-index --find-links wheelhouse
	# "C:\Users\foranw\AppData\Local\PsychoPy3\python.exe" -m pip install -e . --user
