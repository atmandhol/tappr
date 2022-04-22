import os
import json
import typer
import string
import random

from tappr.modules.utils import constants

"""
CLI Color Coding Standard:
- DEBUG statements of the main commands as BOLD yellow
- DEBUG statements of the subcommands as normal yellow
- ERROR in BOLD red
- WARN in BOLD magenta
- SUCCESS in BOLD green
- RUNNING Commands in white
- Important values in BOLD Cyan
"""


# TODO: Add feature to always run some tests at the end even in case of failure
class TestFramework:
    def __init__(self, logger, subprocess_helper):
        self.logger = logger
        self.sh = subprocess_helper

    # noinspection PyUnresolvedReferences
    def run_tests(self, test_file: str, output="stdout"):
        # Build context
        try:
            test_data = json.loads(open(test_file, "r").read())
        except Exception:
            self.logger.error(
                f"Invalid json test file structure in file {test_file}. Make sure it follows the following structure.\n"
                '{"tests": [], "context": {}}'
            )
            raise typer.Exit(-1)

        tests = test_data["tests"]
        context = test_data["context"]
        context = self.prep_context(context=context)
        context[constants.OUTPUT] = output

        for test in tests:
            self.logger.debug(f"Running {test.get('name')}")
            out_agg = str()
            for cmd in test.get("run"):
                if str(cmd).startswith("SET context"):
                    comp = str(cmd).split(" ")
                    context[comp[2].replace("{$$", "").replace("}", "")] = self.add_values_from_context(comp[3], context=context)
                    continue
                run_cmd = self.add_values_from_context(cmd=cmd, context=context)
                self.logger.debug(f"Running {run_cmd}", bold=False)
                proc, out, err = self.sh.run_proc(cmd=run_cmd)
                self.logger.msg(out.decode())
                self.logger.msg(err.decode())
                out_agg += out.decode() + "\n"

                # check if return code is acceptable
                acceptable_codes = test.get("acceptable_exit_code")
                if acceptable_codes and proc.returncode not in acceptable_codes:
                    self.logger.error(
                        f"Command {run_cmd} returned error code {proc.returncode} which is not in the allowed list {acceptable_codes}"
                    )
                    raise typer.Exit(-1)
                if test.get("fail_on_stderr", True) and err:
                    self.logger.error(f"Command failed. stderr: {err}")
                    raise typer.Exit(-1)

            if test.get("assert_in_output"):
                for item in test.get("assert_in_output"):
                    if item not in out_agg:
                        self.logger.error(f"Value: '{item}' not found in the stdout")
                        raise typer.Exit(-1)

    def prep_context(self, context: dict):
        # Replace {$VAR} with value from env var = VAR
        for item in context:
            if "{$$" in context[item]:
                val = os.environ.get(context[item][3:-1])
                if val is None:
                    self.logger.error(f"env var {context[item][3:-1]} not found!")
                    raise typer.Exit(-1)
                context[item] = val
        return context

    @staticmethod
    def add_values_from_context(cmd: str, context: dict):
        run_cmd = cmd
        for item in context:
            search_str = "{$$%s}" % item
            if search_str in run_cmd:
                run_cmd = run_cmd.replace(search_str, context[item])
            if "{$$python.random}" in run_cmd:
                letters = string.ascii_lowercase
                run_cmd = run_cmd.replace("{$$python.random}", "".join(random.choice(letters) for _ in range(10)))
        return run_cmd
