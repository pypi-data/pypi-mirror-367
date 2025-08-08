#!/usr/bin/env python3
import mhi.pscad

# Launch PSCAD
pscad = mhi.pscad.launch()

# Load the tutorial workspace
pscad.load(r"C:\Users\Public\Documents\PSCAD\5.1.0\Examples\tutorial\Tutorial.pswx", folder=pscad.examples_folder)

# Run all the simulation sets in the workspace
pscad.run_all_simulation_sets()

# Exit PSCAD
pscad.quit()
