# Notes
## Running
1. `run_SOA` is on the "new Eprime" computer's desktop. Use that to launch the task dialog window. It works the same as `L:\Tasks\slipstask\run_SOA.bat`
2. Fill in id number and start
   * The default is to run through all tasks starting with `ID`
   * when the next phase starts on the EPrime computer, instuctions will stop the task form advancing. Any key but the button box or scanner tigger (`1234` and `=`) will forward the instructions.
   * only the scanner trigger (`=`) will advance from the "Waiting for scanner" screen.
3. `q` any time to quit. restart `run_SOA` and select the phase-to-rerun (e.g `DD`) from the drop down to begin there.
   * Check `OnlyOne` to run the phases one at a time if there is likely to be a problem or reason to escape to the desktop between runs.
4. retrieve data from the `slips_data` folder also linked on the Desktop
   * actuall data directory is relative to the task directory: `slipstask/soapy/bin/slips_data/<ID>/<YMD_DATE>`

## Sequence timing

Intial setup has the task sequences all named the same and stopped manually. They can be named and set for a fixed duration.

```
order name dur(seconds)
1     ID   599
2     OD   153
3     SOA  502
4     DD   502
```

see 
```
grep ENDDUR soapy/__init__.py
tail -qn1 soapy/timing/*/6/*csv|cut -d, -f2,9|uniq |sed 's/,/ /;s/PhaseType.//'|while read t d; do echo $t $(echo $d + 6 | bc); done
```
