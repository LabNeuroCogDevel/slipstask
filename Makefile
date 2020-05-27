.PHONY: res

static/js/utils.js: static/js/utils.ts
	tsc -m es2015 --lib esnext,dom $<

res: analysis/txt/res.tsv
analysis/txt/res.tsv: 
	 analysis/fetch.bash > $@
