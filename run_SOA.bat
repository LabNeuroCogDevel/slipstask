@echo off
SET PY="C:\Program Files\PsychoPy3\python.exe"
SET SOA=C:\\Users\\Luna\\Desktop\\slipstask

echo check depends
@echo on
%PY% -c "import typing" || %PY% -m pip install -r %SOA%\\wheelhouse\\requirements.txt --no-index --find-links %SOA%\\wheelhouse
%PY% -c "import soapy"  || %PY% -m pip install -e "%SOA%"

echo running SOAMR
%PY% "%SOA%\\bin\\SOAMR"


@echo off
echo finished
echo.
echo.
echo PUSH ANY KEY TO CLOSE
pause
