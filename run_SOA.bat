@echo off
SET PY="L:\Applications\PsychoPy3\python.exe"
SET SOA=L:\\Tasks\\slipstask\\soapy

echo check depends
@echo on
%PY% -c "import soapy" || %PY% -m pip install -e "%SOA%"

echo running SOAMR
%PY% "%SOA%\\bin\\SOAMR"


@echo off
echo finished
echo.
echo.
echo PUSH ANY KEY TO CLOSE
pause