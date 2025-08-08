#!/usr/bin/env python3
import logging
import os
import mhi.pscad
import mhi.pscad.handler

class BuildEventHandler(mhi.pscad.handler.BuildEvent):

    def __init__(self):
        super().__init__()
        self._start = {}

    def _build_event(self, phase, status, project, elapsed, **kwargs):

        key = (project, phase)
        if status == 'BEGIN':
            self._start[key] = elapsed
        else:
            sec = elapsed - self._start[key]
            name = project if project else '[All]'
            LOG.info("%s %s: %.3f sec", name, phase, sec)


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
LOG.info("Launching: %s", version)
pscad = mhi.pscad.launch(minimize=True, version=version, x64=x64)

if pscad:

    # Create a dictionary of new settings to apply
    new_settings = {}

    # Get Fortran compiler versions
    fortrans = pscad.setting_range('fortran_version')
    LOG.info("Fortran versions: %s", fortrans)

    # Skip 'GFortran' compilers, if other choices exist
    vers = [ver for ver in fortrans if 'GFortran' not in ver]
    if len(vers) > 0:
        fortrans = vers

    LOG.info("   After filtering: %s", fortrans)

    # Order the remaining compilers, choose the last one (highest revision)
    fortran = sorted(fortrans)[-1]
    new_settings['fortran_version'] = fortran
    LOG.info("   Selected Fortran version: %r", fortran)

    if pscad.version_number >= (5, 1) and 'Intel' in fortran:
        # In PSCAD 5.1+ w/ Intel Fortran compiler, a Visual Studios linker
        # selection required.
        linkers = pscad.setting_range('c_version')
        LOG.info("Linker versions: %s", linkers)
        linkers = {ver for ver in linkers if ver.startswith('VS')}
        LOG.info("   After filtering: %s", linkers)
        linker = sorted(linkers)[0]
        new_settings['c_version'] = linker
        LOG.info("   Selected Linker version: %r", linker)

    # Get all installed Matlab versions
    matlabs = pscad.setting_range('matlab_version')
    LOG.info("Matlab versions: %s", matlabs)

    # Get the highest installed version of Matlab:
    matlab = sorted(matlabs)[-1] if matlabs else ''
    new_settings['matlab_version'] = matlab
    LOG.info("   Selected Matlab version: %r", matlab)

    pscad.settings(**new_settings)

    # Locate the tutorial directory
    tutorial_dir = os.path.join(pscad.examples_folder, "tutorial")
    LOG.info("Tutorial directory: %s", tutorial_dir)

    try:
        # Load only the 'voltage divider' project
        pscad.load("vdiv.pscx", folder=tutorial_dir)

        # Get the list of simulation sets
        sim_sets = pscad.simulation_sets()
        if len(sim_sets) > 0:
            LOG.info("Simulation sets: %s", sim_sets)

            # For each simulation set ...
            for sim_set_name in sim_sets:
                # ... run it
                LOG.info("Running simulation set '%s'", sim_set_name)
                sim_set = pscad.simulation_set(sim_set_name)
                sim_set.run()
                LOG.info("Simulation set '%s' complete", sim_set_name)
        else:
            # For each tutorial case ...
            for project in pscad.cases():
                LOG.info("Running '%s' (%s)",
                         project.name,
                         project.parameters()['description'])
                project.run(BuildEventHandler());
                LOG.info("Run '%s' complete", project.name)

    finally:
        # Exit PSCAD
        pscad.quit()

else:
    LOG.error("Failed to launch PSCAD")
