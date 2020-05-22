static/js/utils.js: static/js/utils.ts
	tsc -m es2015 --lib esnext,dom $<
