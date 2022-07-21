import os
import json
import typer
import string
import random

from tappr.modules.utils import constants


# TODO: Add feature to always run some tests at the end even in case of failure
class TestFramework:
    def __init__(self, logger, subprocess_helper, ui_helper):
        self.logger = logger
        self.sh = subprocess_helper
        self.ui_helper = ui_helper

    # noinspection PyUnresolvedReferences
    def run_tests(self, test_file: str, output="stdout", state=None):
        # Build context
        try:
            test_data = json.loads(open(test_file, "r").read())
        except Exception:
            self.logger.msg(
                f":broken_heart: Invalid json test file structure in file {test_file}. Make sure it follows the following structure.\n" '{"tests": [], "context": {}}',
                bold=False,
            )
            raise typer.Exit(-1)

        tests = test_data["tests"]
        context = test_data["context"]
        context = self.prep_context(context=context)
        context[constants.OUTPUT] = output

        for test in tests:
            self.logger.msg(f":test_tube: Running test [yellow]{test.get('name')}[/yellow]", bold=False)
            out_agg = str()
            for cmd in test.get("run"):
                if str(cmd).startswith("SET context"):
                    comp = str(cmd).split(" ")
                    context[comp[2].replace("{$$", "").replace("}", "")] = self.add_values_from_context(comp[3], context=context)
                    continue
                run_cmd = self.add_values_from_context(cmd=cmd, context=context)

                proc, out, err = self.ui_helper.progress(cmd=run_cmd, message=":hourglass: Running", state=state)
                out_agg += out.decode() + "\n"

                # check if return code is acceptable
                acceptable_codes = test.get("acceptable_exit_code")
                if acceptable_codes and proc.returncode not in acceptable_codes:
                    self.logger.msg(f":cry: Command [yellow]{run_cmd}[/yellow] returned exit code [red]{proc.returncode}[/red] which is not in the allowed list {acceptable_codes}")
                    raise typer.Exit(-1)
                if test.get("fail_on_stderr", True) and err:
                    self.logger.msg(f":cry: Command failed. stderr: [red]{err}[/red]")
                    raise typer.Exit(-1)

            if test.get("assert_in_output"):
                for item in test.get("assert_in_output"):
                    if item not in out_agg:
                        self.logger.msg(f":cry: [red]test {test.get('name')} failed[/red]. Value: [yellow]{item}[/yellow] not found in the stdout")
                        raise typer.Exit(-1)

    def prep_context(self, context: dict):
        # Replace {$VAR} with value from env var = VAR
        for item in context:
            if "{$$" in context[item]:
                val = os.environ.get(context[item][3:-1])
                if val is None:
                    self.logger.msg(f":stop_sign: env var [yellow]{context[item][3:-1]}[/yellow] not found!")
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
