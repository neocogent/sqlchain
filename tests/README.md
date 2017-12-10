### sqlChain Test Suite

##### Recent Updates (v0.2.5)

Initial test suite commit. This is just a beginning in trying to make everything more robust. I hope to expand it's completeness over time.

The current test suite is based on using the [pytest](https://docs.pytest.org/en/latest/contents.html) module. The live tests also require the [deepdiff](https://github.com/seperman/deepdiff) module. 

There are 3 classes of test here:

- tests that can run standalone on the static codebase

    These try to assess whether module functions behave as expected independently and should be run before release. So far they only focus on the sqlchain.util module but I hope to extend wherever it may be worthwhile.
    
- tests that depend on a transient memory-only version of the main database

    These still typically test on a unit basis but require some database interaction. To run they require the mysqldb module and a running mysql server plus a valid admin level user and password. The default user/pwd is hard coded as "root:root", making it a little easier for test runs in non-secure environments. A `--dbuser` option allows setting custom values for a test system, eg. `pytest --dbuser adm:hoochiedoll`, assuming you've created this user/pwd previously for testing.
    
- live tests that depend on a installed and working system (to at least some extent).

    These test actual operation and try to detect errors or discrepancies under (close to) real operating conditions. They also include some profiling functions to assess performance. So far this is focusing on sqlchain-api tests comparing sqlchain returned values to a sqlite database of reference results collected from other api-server resources. 
    
    The `mklivetestdb` utility can be used to collect random data from other servers that is stored in livetest.db (a sqlite3 db file). This data is used as for comparison in tracking down abherant behaviour. Live tests are skipped by default and can be enabled with the `--runlive` option. Two other options add more flexibility: `--server` for setting the live server to connect with, and `--append` to disable the default cleaning of previous test data for each new run. eg. `--server localhost:8085/api` (the default, note it includes api path).

##### Command Summary

These assume sqlchain is installed with setup.py or pip, and you are in the sqlchain root directory of a cloned repository. 

`pytest` (will run any test cases it finds in the tests directory, skips any that cannot run for "reasons")

`pytest -rs`  (run tests and show reasons why if some are skipped)

`pytest --dbuser root:mysecretpwd`  (run db test cases)

`pytest --runlive`    (run live api tests with clean test results db)

`pytest --runlive --server mytestrig.info:8989/rig-api/`   (run live api tests against remote server)

`pytest --runlive --append`   (run live api tests but keep old data)

