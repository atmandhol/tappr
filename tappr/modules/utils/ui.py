from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, TextColumn


class UI:
    def __init__(self, subprocess_helper, logger):
        self.sh = subprocess_helper
        self.logger = logger

    def progress(self, cmd, message, state):
        self.logger.msg(f"Running: {cmd}", bold=False) if state["verbose"] else None
        proc, out, err = None, None, None
        with Progress(TextColumn(f"{message}"), SpinnerColumn(spinner_name="point"), TimeElapsedColumn(), transient=True) as progress:
            task = progress.add_task("", total=1)
            while not progress.finished:
                proc, out, err = self.sh.run_proc(f"{cmd}")
                progress.update(task_id=task, advance=1)

        self.logger.msg(f"\n{out.decode()}", bold=False) if state["verbose"] and out else None
        self.logger.msg(f"\n{err.decode()}", bold=False) if state["verbose"] and err else None
        return proc, out, err

    def sh_call(self, cmd, msg, spinner_msg, error_msg, state):
        self.logger.msg(msg, bold=True)
        proc, _, _ = self.progress(cmd=cmd, state=state, message=spinner_msg)
        if proc.returncode != 0 and error_msg is not None:
            self.logger.msg(error_msg)
        return proc.returncode
