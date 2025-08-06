#!/usr/bin/env python3
"""Debug CLI exit codes."""

from typer.testing import CliRunner
from pyextractit.__main__ import app

def test_exit_codes():
    runner = CliRunner()
    
    # Test invalid regex
    result = runner.invoke(app, ['extract', 'dummy.zip', '[invalid'])
    print('Exit code for invalid regex:', result.exit_code)
    print('Output:', result.stdout)
    print('Error:', result.stderr)
    print()
    
    # Test invalid max-depth
    result2 = runner.invoke(app, ['extract', 'dummy.zip', '.*\\.txt$', '--max-depth', '0'])
    print('Exit code for invalid max-depth:', result2.exit_code)
    print('Output:', result2.stdout)
    print('Error:', result2.stderr)

if __name__ == "__main__":
    test_exit_codes()
