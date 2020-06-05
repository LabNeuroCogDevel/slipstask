.PHONY: res test always

static/js/utils.js: static/js/utils.ts
	tsc -m es2015 --lib esnext,dom -d $<
	tsc -b 

res:  analysis/txt/task.tsv
analysis/txt/res.json: always
	 analysis/fetch.bash > $@

analysis/txt/task.tsv: analysis/txt/res.json
	analysis/json2tsv.bash $<

test: tests/.res.tap
tests/.res.tap: $(wildcard tests/*js)
	# npm test
	jest --json 2>/dev/null | jest-json-to-tap > $@
