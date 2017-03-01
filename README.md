run_over_amplitudes.sh runs the data aquisition software (measure_test.py) with the given frequency and distance parameters over the current pulse amplitude range of 60-160 mA, with an increment of 10 mA. It also includes a background reading for each run.
The format for running this program from the terminal is
sudo ./run_over_amplitudes.sh FREQUENCY DISTANCE
With FREQUENCY and DISTANCE replaced with the relevant values

Running measure_test through python is more flexible, but the parameters can't currently be changed mid-run. The general format and required parameters are
sudo python measure_test.py BASENAME -a CURRENTAMPLITUDE -f FREQUENCY -r MEASUREMENTRANGE (2E-9) -di DISTANCE
Note that there are more possible parameters, accessed with the -h or --help params

The UVLEDDataCompile jar allows the user to select any number of .csv files (such as those created by measure_test) and, if they are formatted correctly, creates a single .csv file summarizing each of the chosen data files.

Need to use tr '\r' '\n' < dataset.csv > dataset.csv
to translate mac/windows created .csv's to Unix
