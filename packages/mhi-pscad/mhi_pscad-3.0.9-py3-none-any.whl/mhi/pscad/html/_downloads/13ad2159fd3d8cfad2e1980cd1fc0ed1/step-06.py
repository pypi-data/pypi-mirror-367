#!/usr/bin/env python3
import logging
import os
import mhi.pscad

# Log 'INFO' messages & above.  Include level & module name.
logging.basicConfig(level=logging.INFO,
                    format="%(levelname)-8s %(name)-26s %(message)s")

# Ignore INFO msgs from automation (eg, mhi.pscad, mhi.common, ...)
logging.getLogger('mhi').setLevel(logging.WARNING)

LOG = logging.getLogger('main')

versions = mhi.pscad.versions()
LOG.info("PSCAD Versions: %s", versions)

# Skip any 'Beta' versions
versions = [(ver, x64) for ver, x64 in versions if "Beta" not in ver]

# Skip versions prior to '5.0'
versions = [(ver, x64) for ver, x64 in versions if not ver.startswith("4.")]

# Skip any 32-bit versions, if other choices exist
vers = [(ver, x64) for ver, x64 in versions if x64]
if len(vers) > 0:
    versions = vers

LOG.info("   After filtering: %s", versions)

# Of any remaining versions, choose the "lexically largest" one.
version, x64 = sorted(versions)[-1]
LOG.info("   Selected PSCAD version: %s %d-bit", version, 64 if x64 else 32)

# Launch PSCAD
pscad = mhi.pscad.launch(minimize=True, version=version, x64=x64)

if pscad:

    # Locate the tutorial directory
    tutorial_dir = os.path.join(pscad.examples_folder, "tutorial")
    LOG.info("Tutorial directory: %s", tutorial_dir)

    try:
        # Load the tutorial workspace
        pscad.load("Tutorial.pswx", folder=tutorial_dir)

        # Run all the simulation sets in the workspace
        pscad.run_all_simulation_sets()

    finally:
        # Exit PSCAD
        pscad.quit()

else:
    LOG.error("Failed to launch PSCAD")
