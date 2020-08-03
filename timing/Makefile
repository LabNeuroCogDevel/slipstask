.make:
	mkdir .make

.make/times.ls: ./gentiming.py | .make
	./gentiming.py
	mkls $@ 'seeded/*/*'

seeded/tr1_dur1.5_454total.txt: .make/times.ls
	./collect
