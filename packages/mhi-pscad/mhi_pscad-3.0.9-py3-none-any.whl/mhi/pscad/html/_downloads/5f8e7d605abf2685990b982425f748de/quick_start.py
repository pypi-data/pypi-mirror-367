#!/usr/bin/env python3
import mhi.pscad

pscad = mhi.pscad.launch()

pscad.load("tutorial/Tutorial.pswx", folder=pscad.examples_folder)
pscad.run_all_simulation_sets()

pscad.quit()
