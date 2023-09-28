"# python-structured-prog"

This repository is a python script that can calculate electrical outputs for any circuit.
This script works by using a .net input file that describes a circuit using node connections and a description of the component value either in resistance or conductance based on whether it is a uniform component or a capacitor/inductor.
The source is also described along with any other internal resistance components and circuit behavioural charactaristics (frequencies).

Please see an example .net file inside the directory "TESTFILES" for an overview on how to create a circuit. NOTE: parallel circuits can be described by sharing node connections.

The output results in a .csv file listing all the input source parameters along with any electrical output (voltage, amperage).
