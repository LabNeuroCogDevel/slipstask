.PHONY: res test always

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
	git diff|sed -n s/^\+[^+]//p|cut -f1,3|sort |uniq -c|sort -k2,1|cut -f1|uniq -c|sort -k2n|egrep '\w{31}$$'
test: tests/.res.tap
tests/.res.tap: $(wildcard tests/*js)
	# npm test
	jest --json 2>/dev/null | jest-json-to-tap > $@
