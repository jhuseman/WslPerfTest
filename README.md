# WslPerfTest

A python script to test file access performance in Windows Subsystem for Linux (WSL), primarily for the purposes of evaluating improvements of WSL2 over WSL1.

If running on Windows, the script will by default run the same set of tests inside of WSL (a list of distros can be specified with the -d argument) for comparison.

If running on WSL, the script will by default run the same set of tests in native Windows for comparison.

The tests are conducted by default accessing Windows files from WSL, accessing WSL files from Windows, accessing files natively in Windows, and accessing "native" WSL files inside of WSL.

The script currently performs two main tests (can be expanded by modifying the run_test function):
- largefile: writes all of the data (of the specified size) to a single file, loads that data back in from the file, makes a copy of the file, renames the copied file, then deletes both copies of the file
- smallfile: writes the data (totalling to the specified size) in many small files (256 bytes each), makes a copy of the directory, then deletes both copies of the directory

Each step of all of the tests are timed, and saved to a CSV or JSON file. The column names for these steps are as follows:
- generate - create a buffer of data to store in the files for the test - continually increasing (modulus 256) sequence of bytes
- write - save the entire buffer of data to a file - uses python file pointers
- read - load back in the data from the file created in the "write" step - uses python file pointers
- copy - make a copy of the file created in the "write" step - uses `shutil.copy`
- rename - renames the file created in the "copy" step - uses `os.rename`
- delete - deletes the file created in the "write" step - uses `os.remove`
- delete2 - deletes the file created in the "copy" step - uses `os.remove`
- mkdir - create an empty directory - uses `os.mkdir`
- small_write - write several (enough to total the size of the buffer) small files (containing the first 256 bytes of data in the buffer) in the directory created in the "mkdir" step - uses python file pointers
- copy_dir - make a copy of the directory created in the "mkdir" step - uses `shutil.copytree`
- rm_rec - recursively deletes the directory created in the "mkdir" step - uses `shutil.rmtree`
- rm_rec2 - recursively deletes the directory created in the "copy_dir" step - uses `shutil.rmtree`

The row names (first column) of the generated CSV file are of the form `<src>/<dest>`, where `<src>` refers to the platform/distro the script is running in (and thus file accesses are performed from), and `<dest>` refers to the platform/distro which "owns" the filesystem which the files are created in.  For example `Windows/Windows` refers to files accessed natively inside of Windows, while `Ubuntu/Windows` refers to files accessed inside of `/mnt/c` from the distro "Ubuntu" running in WSL.

command-line usage:
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


example commands (On a system with two distributions, named "Ubuntu" and "Ubuntu_WSL2_test"):
```bash
# example of all arguments
$ python WslPerfTest.py -d Ubuntu,Ubuntu_WSL2_test -c yes -x yes -o results\results256K.csv -s 256K -t csv -p largefile,smallfile

# runs same as above
$ python WslPerfTest.py -d Ubuntu,Ubuntu_WSL2_test -o results\results256K.csv -s 256K -t csv

# creates a JSON file output instead, only running the "largefile" test
$ python WslPerfTest.py -d Ubuntu,Ubuntu_WSL2_test -o results\results100M_largefile.json -s 100M -t json -p largefile
```
