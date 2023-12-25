def setup(required):
    import subprocess
    import sys
    import pkg_resources
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed

    if missing:
        # implement pip as a subprocess:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])
    else:  # Update all required packages
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', *required])
