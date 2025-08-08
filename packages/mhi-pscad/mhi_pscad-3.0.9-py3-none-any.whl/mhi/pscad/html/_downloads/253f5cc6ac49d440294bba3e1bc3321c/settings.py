#!/usr/bin/env python3
import mhi.pscad

pscad = mhi.pscad.launch(minimize=True)

for key, value in sorted(pscad.settings().items()):
    print(f"{key:>33}: {value!r}")

pscad.quit()
