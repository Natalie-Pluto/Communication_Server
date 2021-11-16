#Tests

---

## Description

`runTests.sh`  -> Bash script for running the tests

`startServer.py` -> Program for starting the server

`serverTest.py` -> Unittests

`test_result.json` -> Test report


##How to run the tests:

`chmod +rwx runTests.sh`

`./runTests.sh`

##Generate Test Report

A test report will be generated automatically after running the tests.

`test_result.json`

##Generate Coverage Report

`coverage report -m server.py`

### Coverage Report For Last Submission
```
Name        Stmts   Miss  Cover   Missing
-----------------------------------------
server.py     141     24    83%   42, 138-140, 190-203, 207-210, 220-224, 231-234
-----------------------------------------
TOTAL         141     24    83%
```



