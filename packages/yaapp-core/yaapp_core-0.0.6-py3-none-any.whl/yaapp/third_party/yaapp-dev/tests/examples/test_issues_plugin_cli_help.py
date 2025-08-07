import sys
import subprocess


import glob
import sys
import subprocess


def test_all_example_clis_expose_commands():
    """
    Run each example under examples/plugins and assert it returns --help successfully.
    """
    # Find all plugin example scripts
    paths = glob.glob('examples/plugins/*/app.py')
    assert paths, 'No plugin example scripts found'

    for script in paths:
        result = subprocess.run(
            [sys.executable, script, '--help'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        assert result.returncode == 0, f"Help invocation failed for {script}: {result.stderr}"
