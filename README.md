# SAT-solver

SAT solver for Logic in computer science course.

There are two versions of the algorithm: DPLL and CDCL.
The CDCL algorithm is generally faster so this version should be run. 

+ DPLL algorithm can be run using the command: python SAT_solver.py "path to input-file" "path to output-file"
+ CDCL algorithm can be run using the command: python SAT_solver_CDCL.py "path to input-file" "path to output-file"

The tests are stored in the tests folder, along with the script generate_cnf.py for generating random SAT problems.

The test we want to showcase is the rand100.txt test that can be found in tests/random/ folder.
We show this test because it showcases the difference between DPLL and CDCL algorithms since DPLL needs 45.113 seconds
and CDCL 0.2 seconds.

Run our example using the command:
`python SAT_solver_CDCL.py tests/random/rand100.txt out.txt` 
