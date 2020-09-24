@echo off
SET PY="C:\Program Files\PsychoPy3\python.exe"
SET SOA=C:\\Users\\Luna\\Desktop\\slipstask

REM echo check depends
REM @echo on
REM %PY% -c "import typing" || %PY% -m pip install -r "%SOA%\\wheelhouse\\requirements.txt" --no-index --find-links "%SOA%\\wheelhouse" --user
REM %PY% -c "import soapy"  || %PY% -m pip install -e "%SOA%" --user

echo running SOAMR
%PY% "%SOA%\\soapy\\\\bin\\SOAMR"


@echo off
echo finished
echo.
echo.
echo PUSH ANY KEY TO CLOSE
pause
