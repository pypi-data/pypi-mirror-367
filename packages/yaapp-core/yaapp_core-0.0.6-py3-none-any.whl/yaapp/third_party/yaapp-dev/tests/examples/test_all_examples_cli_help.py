import glob
import subprocess
import sys


def test_all_examples_cli_help():
    """
    Ensure every example script supports the --help option without error.
    """
    # Collect example entrypoints (app.py & standalone scripts in examples/)
    patterns = [
        'examples/**/*.py',
    ]
    scripts = []
    for pat in patterns:
        for path in glob.glob(pat, recursive=True):
            # Skip README or non-executable modules
            name = path.split('/')[-1]
            if name in ('app.py', 'issues_example.py', 'configuration_example.py', 'execution_strategies_example.py', 'proxy_client.py', 'streaming-demo.py', 'task-manager.py', 'test_server.py'):
                scripts.append(path)
    assert scripts, 'No example scripts found'

    for script in scripts:
        result = subprocess.run(
            [sys.executable, script, '--help'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        assert result.returncode == 0, f"Help failed for {script}: {result.stderr or result.stdout}"
