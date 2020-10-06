@echo off
REM location of python and task on MRRC "Eprime" presentation computers
SET PY="C:\Program Files\PsychoPy3\python.exe"
SET SOA=C:\\Users\\Luna\\Desktop\\slipstask

REM location at lab 
IF NOT EXIST %PY% (
    @echo on
    SET PY="L:\Applications\PsychoPy3\python.exe"
    SET SOA=L:\\Tasks\\slipstask
    %PY% -c "import soapy; assert soapy.__version__=='0.1.0'"  || %PY% -m pip install -e "%SOA%" --user -U
)


REM echo check depends
REM @echo on
REM %PY% -c "import typing" || %PY% -m pip install -r "%SOA%\\wheelhouse\\requirements.txt" --no-index --find-links "%SOA%\\wheelhouse" --user
REM %PY% -c "import soapy"  || %PY% -m pip install -e "%SOA%" --user

echo running SOABlk
%PY% "%SOA%\\soapy\\\\bin\\SOABlk"


@echo off
echo finished
echo.
echo.
echo PUSH ANY KEY TO CLOSE
pause
