//** This is a little guideline where there are some indications to run the different models **//

The repository is built with the idea that all the scripts can be run by launching python scripts into the src folder. It is important to preserve the structure repository to keep working the reading and writing procedure. 

MINIZINC: 

In the 'src/cp folder':

1. To test the baseline mzn model, run the 'main_cp.py' script. 
2. To test the rotation mzn model, run 'main_cp_rot.py' script.
3. To test the geost mzn model, run 'main_geost.py' script.

The output is divided into other folders inside the 'out/cp' directory, one for each approach. 
In order to try the annotations, they have to be uncommented in the corresponding mzn file, changing (just for clarity) the output folder that are defined as follows: 
- 'out/cp/cp_vanilla' --> no annotations output
- 'out/cp/cp_ann' --> with annotation output
- 'out/cp/cp_rot' --> annotation + restart output

SMT: 

In the 'src/smt folder':

1. To test the baseline SMT model, run 'smt_solution.py'
2. To test the rotation SMT model, run 'smt_solution_rot.py'

The output is divided into other folders inside the 'out/smt' directory, that are defined as follows:
- 'out/smt/smt' --> baseline model output
- 'out/smt/smt_rot' --> rotation model output



