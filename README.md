# WslPerfTest

A python script to test file access performance in Windows Subsystem for Linux (WSL)

usage:
```
python WslPerfTest.py [-h] [-d DISTRO] [-c CROSS_TEST] [-x CROSS_PERF_TEST]
                      [-o OUTPUT] [-s SIZE] [-t OUTPUT_TYPE]
                      [-p PERFORMANCE_TESTS]

optional arguments:
  -h, --help            show this help message and exit
  -d DISTRO, --distro DISTRO
                        Comma-separated list of distros to run the test on.
                        Ignored if run from inside WSL (instead runs test in
                        Windows). Defaults to Ubuntu.
  -c CROSS_TEST, --cross_test CROSS_TEST
                        Indicates whether the test should also be conducted in
                        WSL if run from Windows or conducted in Windows if run
                        from WSL. Any other flag than "true", "yes", "t", or
                        "y" (case insensitive) is interpreted as False.
                        Defaults to True.
  -x CROSS_PERF_TEST, --cross_perf_test CROSS_PERF_TEST
                        Indicates whether the test should also be conducted in
                        a WSL folder if run from Windows or conducted in a
                        Windows folder if run from WSL. Any other flag than
                        "true", "yes", "t", or "y" (case insensitive) is
                        interpreted as False. Defaults to True.
  -o OUTPUT, --output OUTPUT
                        Indicates a file that the output results should be
                        saved to. If omitted, or set to "-", outputs to
                        STDOUT.
  -s SIZE, --size SIZE  The size of file that should be generated for the
                        test. Should be a string in the format "1G", "128M",
                        or "64K", etc.
  -t OUTPUT_TYPE, --output_type OUTPUT_TYPE
                        The type of output that should be created. Should be
                        one of "json" or "csv".
  -p PERFORMANCE_TESTS, --performance_tests PERFORMANCE_TESTS
                        Comma-separated list of the specific tests to run. For
                        all tests, should be "largefile,smallfile".
```
