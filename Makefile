.PHONY: res test always

static/js/utils.js: static/js/utils.ts
	tsc -m es2015 --lib esnext,dom -d $<
	tsc -b 

res:  analysis/txt/res.tsv
analysis/txt/res.tsv: always
	 analysis/fetch.bash > $@

test: tests/.res.tap
tests/.res.tap: $(wildcard tests/*js)
	# npm test
	jest --json 2>/dev/null | jest-json-to-tap > $@
