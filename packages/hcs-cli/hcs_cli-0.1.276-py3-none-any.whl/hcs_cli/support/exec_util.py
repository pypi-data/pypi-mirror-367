import os
import subprocess

import click


def exec(cmd, log_error=True, raise_on_error=True, inherit_output=False, cwd=None):
    click.echo(click.style(f"COMMAND: {cmd}", fg="bright_black"))

    env = os.environ.copy()
    env["HCS_CLI_CHECK_UPGRADE"] = "false"

    if inherit_output:
        result = subprocess.run(
            cmd.split(" "),
            env=env,
        )
    else:
        result = subprocess.run(cmd.split(" "), capture_output=True, text=True, env=env, cwd=cwd)

    if result.returncode != 0:
        if log_error:
            click.echo(f"  RETURN: {result.returncode}")
            if not inherit_output:
                stdout = result.stdout.strip()
                stderr = result.stderr.strip()
                if stdout:
                    click.echo(f"  STDOUT:      {stdout}")
                if stderr:
                    click.echo(f"  STDERR:      {stderr}")
        if raise_on_error:
            raise click.ClickException(f"Command '{cmd}' failed with return code {result.returncode}.")
    return result
