import typer
import importlib

app = typer.Typer(
    help="Workflow management commands.",
    pretty_exceptions_enable=False,
    rich_markup_mode=None
)


def lazy(func_path: str):
    mod, fn = func_path.rsplit(":", 1)
    def _inner(*args, **kwargs):
        return getattr(importlib.import_module(mod), fn)(*args, **kwargs)
    return _inner

app.command()(lazy("quansys.cli.submit_cmd:submit"))
app.command()(lazy("quansys.cli.run_cmd:run"))
app.command()(lazy("quansys.cli.example_cmd:example"))
