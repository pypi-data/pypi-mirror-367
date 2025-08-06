from __future__ import annotations

import dataclasses
import enum
import importlib
import logging
import os
import pathlib
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
import typing

from rich.logging import RichHandler

if typing.TYPE_CHECKING:
    from rich.console import Console

_logger = logging.getLogger("odoo_runbot")
# prefix for all env variable to force interactive input

RUNBOT_PREFIX = "RUNBOT_"
SET_ODOO_PREFIX = "SET_ODOO_"


def _apply_default_if_none(data_class: object) -> None:
    if not dataclasses.is_dataclass(data_class):
        err = f"Only valid call for dataclasses {type(data_class)}"
        raise ValueError(err)
    # Loop through the fields
    for field in dataclasses.fields(data_class):
        # If there is a default and the value of the field is none we can assign a value
        if not isinstance(field.default, type(dataclasses.MISSING)) and getattr(data_class, field.name) is None:
            setattr(data_class, field.name, field.default)
        if not isinstance(field.default_factory, type(dataclasses.MISSING)) and getattr(data_class, field.name) is None:
            setattr(data_class, field.name, field.default_factory())


_LEVEL_MAPPING = {
    logging.DEBUG: "[blue]DEBUG[/blue]",
    logging.INFO: "[green]INFO[/green]",
    logging.WARNING: "[yellow]WARNING[/yellow]",
    logging.ERROR: "[red]ERROR[/red]",
    logging.CRITICAL: "[bold red]CRITICAL[/bold red]",
}


class RunbotEnvironment:
    """The complete env of the runbot"""

    UNIQUE_ID: str
    """Unique string id, based on Gitlab CI_JOB_ID and CI_NODE_INDEX in case of parallel"""
    ODOO_VERSION: str
    """
    The Odoo version to test, provided by the image where the runbot run.
    """
    GITLAB_READ_API_TOKEN: str
    """
    The token used to access the Gitlab API.
    This token is taken from `CI_JOB_TOKEN` or `PERSONAL_GITLAB_TOKEN` or `GITLAB_TOKEN` environment variable.
    In GitLab CI job be sure `CI_JOB_TOKEN` have the correct right. [https://docs.gitlab.com/ee/ci/jobs/ci_job_token.html]
    """

    def __init__(self, environ: dict[str, str], *, workdir: pathlib.Path | None = None, verbose: bool = False) -> None:
        self.environ = environ
        self.verbose = verbose or environ.get("RUNBOT_VERBOSE", False)
        self.CI_COMMIT_REF_NAME = environ.get("CI_COMMIT_REF_NAME")
        self.CI_MERGE_REQUEST_TARGET_BRANCH_NAME = environ.get("CI_MERGE_REQUEST_TARGET_BRANCH_NAME")
        self.CI_PROJECT_NAME = environ.get("CI_PROJECT_NAME")
        self.CI_JOB_TOKEN = environ.get("CI_JOB_TOKEN")
        self.CI_DEPLOY_TOKEN = environ.get("CI_DEPLOY_TOKEN")
        self.CI_PROJECT_PATH = environ.get("CI_PROJECT_PATH")
        self.CI_API_V4_URL = environ.get("CI_API_V4_URL")
        self.CI_SERVER_URL = environ.get("CI_SERVER_URL")
        self.ODOO_VERSION = str(environ.get("ODOO_VERSION"))
        self.UNIQUE_ID = "-".join(
            [
                "job",
                environ.get("CI_JOB_ID") or environ.get("RUNBOT_RANDOM_ID", "0"),
                environ.get("CI_NODE_INDEX", "1"),
            ],
        )
        self.GITLAB_READ_API_TOKEN = (
            environ.get("GITLAB_READ_API_TOKEN") or environ.get("CI_JOB_TOKEN") or environ.get("GITLAB_TOKEN")
        )
        self.in_ci = "CI" in os.environ
        self.abs_curr_dir = pathlib.Path.cwd().absolute().resolve()
        if workdir:
            self.abs_curr_dir = workdir.resolve().absolute()
        self.result_path = self.abs_curr_dir / "runbot_result"
        self.ODOO_RC = environ.get("ODOO_RC", str(self.abs_curr_dir / "odoo-config.ini"))
        self.environ["DATABASE"] = "_".join(["runbot_db", self.UNIQUE_ID.replace("-", "_")])
        self.environ["DB_NAME"] = self.environ["DATABASE"]
        try:
            self.result_path.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            if not self.result_path.exists():
                _logger.warning("Can't create folder %s", str(self.result_path))

    def chdir(self, new_dir: pathlib.Path | None) -> None:
        if new_dir:
            os.chdir(new_dir)
            self.__dict__.pop("project_config", None)

    @property
    def CI_PROJECT_DIR(self) -> pathlib.Path:  # noqa: N802
        """Returns: The CI_PROJECT_DIR provide by Gitlab CI as a [pathlib.Path][] object."""
        return pathlib.Path(os.environ["CI_PROJECT_DIR"])

    def setup_logging_for_runbot(self, console: Console) -> None:
        level = logging.DEBUG if self.verbose else logging.INFO
        rich_handler = RichHandler(
            level, console=console, rich_tracebacks=True, enable_link_path=not self.environ.get("CI", False)
        )
        rich_handler.addFilter(logging.Filter("odoo_runbot"))
        _logger = logging.getLogger("odoo_runbot")
        _logger.addHandler(rich_handler)
        _logger.setLevel(level)

    def check_ok(self) -> bool:
        res = True
        if not self.abs_curr_dir.joinpath("pyproject.toml").exists():
            _logger.error("Workdir %s don't exist", self.abs_curr_dir)
            res = False
        elif not RunbotToolConfig.get_toml_data(self.abs_curr_dir.joinpath("pyproject.toml")):
            _logger.error("No `tool.runbot` config in %s", self.abs_curr_dir.joinpath("pyproject.toml"))
            res = False
        try:
            from odoo import release  # noqa: PLC0415

            if release.version < "12.0":
                _logger.error("This runbot can't run the test from Odoo less than 12.0")
                res = False
        except ImportError:
            pass

        return res

    def print_info(self) -> None:
        _logger.info("Run in %s", str(self.abs_curr_dir))
        _logger.info("Test result in %s", str(self.result_path))
        if os.getenv("ODOO_DEPENDS"):
            _logger.error("Il ne faut plus utiliser `ODOO_DEPENDS` ni même la renseigner dans le runbot.")
            _logger.error("Il faut au lieu utiliser les variables `ADDONS_GIT_XXX` supportée par `addons-installer`")
        _logger.info("Odoo version: %s", self.ODOO_VERSION)
        _logger.info("Odoo config file: %s", self.ODOO_RC)


@dataclasses.dataclass()
class RunbotExcludeWarning:
    """Container for a regex to exclude in the log
    Attributes:
        name (str): A name for this regex.
            Allow to print if this regex found a warning to exclude
        level (str) : The level of the logger expected. WARNING by default
        min_match (int): Min occurrence of this warning in the log. The runbot should failed otherwaise
        max_match (int): Max occurrence of this warning in the log. The runbot should failed otherwaise
        regex (str): A regular expression to exclude
    """

    name: str
    regex: str
    logger: str = dataclasses.field(default="")
    level: str = dataclasses.field(default=logging.getLevelName(logging.WARNING))
    min_match: int = dataclasses.field(default=1)
    max_match: int = dataclasses.field(default=1)

    def __post_init__(self) -> None:
        _apply_default_if_none(self)
        self.max_match = min(max(self.max_match, self.min_match), 100) if self.max_match > 0 else 0
        self.min_match = max(min(self.min_match, self.max_match), 0) if self.max_match > 0 else 0


@dataclasses.dataclass()
class RunbotPyWarningsFilter:
    """Dataclass storing wich py.warnings to filter"""

    name: str
    action: str
    message: str | None = dataclasses.field(default=None)
    category: str | None = dataclasses.field(default=None)

    def __post_init__(self) -> None:
        _apply_default_if_none(self)


class StepAction(enum.Enum):
    TESTS = "tests"
    INSTALL = "install"


@dataclasses.dataclass()
class RunbotStepConfig:
    """Contain the config for one warmup"""

    name: str
    modules: list[str]
    action: StepAction = dataclasses.field(default=StepAction.TESTS)
    test_tags: list[str] = dataclasses.field(default_factory=list)
    coverage: bool = dataclasses.field(default=True)
    log_filters: list[RunbotExcludeWarning] = dataclasses.field(default_factory=list)
    allow_warnings: bool = dataclasses.field(default=True)

    def __post_init__(self) -> None:
        _apply_default_if_none(self)


@dataclasses.dataclass()
class RunbotToolConfig:
    """The class containing all the config to run the tests.
    The data are read from the `pyproject.toml` and focus on the `tool.mangono.runbot` section
    """

    include_current_project: bool = dataclasses.field(default=True)
    allowed_warnings: list[str] = dataclasses.field(default_factory=list)
    """Allow all warning (log line with level WARNING, or `py.warnings`) from any python modules"""
    steps: list[RunbotStepConfig] = dataclasses.field(default_factory=list)
    """The config for the test phase (after warmup)"""
    pretty: bool = dataclasses.field(default=True)
    """Use color and pretty printing in log"""
    warning_filters: list[RunbotPyWarningsFilter] = dataclasses.field(default_factory=list)
    """"""
    failfast: bool = dataclasses.field(default=True)

    def __post_init__(self) -> None:
        _apply_default_if_none(self)

    def get_step(self, step_name: str) -> RunbotStepConfig:
        for step in self.steps:
            if step.name == step_name:
                return step
        msg = f"No such step: {step_name}"
        raise KeyError(msg)

    @classmethod
    def load_from_toml(cls, path: pathlib.Path) -> RunbotToolConfig:
        """Create a config from a TOML file path using tomllib or toml depending of the python version.

        Args:
            path:

        Returns:

        """
        return cls.load_from_toml_data(cls.get_toml_data(path))

    @classmethod
    def get_toml_data(cls, path: pathlib.Path) -> dict[str, typing.Any]:
        """Create a config from a TOML file path using tomllib or toml depending of the python version.

        Args:
            path:

        Returns:

        """
        with path.open(mode="rb") as pyproject_toml:
            data = tomllib.load(pyproject_toml)
        return data.get("tool", {}).get("runbot", {})

    @classmethod
    def from_env(cls, env: RunbotEnvironment) -> RunbotToolConfig:
        return cls.load_from_toml(env.abs_curr_dir.joinpath("pyproject.toml"))

    @classmethod
    def load_from_toml_data(cls, runbot_data: dict) -> RunbotToolConfig:
        """Convert the Toml data to a RunbotToolConfig object.

        Args:
            runbot_data: All the data for the sub kley of `runbot.tool`

        Returns: A `RunbotToolConfig` object

        """
        version_log_filter = log_filter_by_odoo_version()
        global_log_filter = cls._get_log_filters(version_log_filter, runbot_data)
        global_pywarnings = warning_filter_by_odoo_version() + [
            RunbotPyWarningsFilter(
                name=py_filter_data.get("name", f"Global PyWarnings Filter {_idx}"),
                action=py_filter_data.get("action"),
                message=py_filter_data.get("message"),
                category=py_filter_data.get("category"),
            )
            for _idx, py_filter_data in enumerate(runbot_data.get("pywarnings-filter", []))
        ]

        cls._inject_default_step(runbot_data)

        steps = []
        for _idx_step, (step_name, step_data) in enumerate(runbot_data.get("step").items()):
            log_filter = cls._get_log_filters(global_log_filter, step_data, step_name=step_name)
            action = cls._get_action(step_name, step_data)
            step_obj = RunbotStepConfig(
                name=step_name,
                allow_warnings=step_data.get("allow-warnings", runbot_data.get("allow-warnings")),
                coverage=action == StepAction.TESTS and step_data.get("coverage", runbot_data.get("coverage")),
                modules=step_data.get("modules", runbot_data.get("modules")),
                action=action,
                test_tags=step_data.get("test-tags"),
                log_filters=log_filter,
            )
            steps.append(step_obj)

        return cls(
            include_current_project=runbot_data.get("include-current-project"),
            pretty=True,
            failfast=runbot_data.get("failfast"),
            steps=steps,
            warning_filters=global_pywarnings,
        )

    @classmethod
    def _inject_default_step(cls, runbot_data: dict[str, typing.Any]) -> None:
        if not runbot_data.get("step"):
            runbot_data["step"] = {
                "default": {
                    "coverage": runbot_data.get("coverage"),
                    "unittest-output": runbot_data.get("unittest-output"),
                    "modules": runbot_data.get("modules"),
                    "action": StepAction.TESTS.name,
                    "test-tags": [],
                    "log-filters": [],
                }
            }

    @classmethod
    def _get_log_filters(
        cls,
        global_log_filter: list[RunbotExcludeWarning],
        step_data: dict[str, typing.Any],
        step_name: str | None = None,
    ) -> list[RunbotExcludeWarning]:
        log_filter = (global_log_filter and global_log_filter[:]) or []
        for _idx_log_filter, data in enumerate(step_data.get("log-filters", []), start=len(log_filter) + 1):
            default_name = f"All Steps - Logger Filter {_idx_log_filter}"
            if step_name:
                default_name = f"Step {step_name} - Logger Filter {_idx_log_filter}"
            _data = data
            if isinstance(data, str):
                _data = {"regex": data}
            log_filter.append(
                RunbotExcludeWarning(
                    name=_data.get("name", default_name),
                    regex=_data["regex"],
                    logger=_data.get("logger"),
                    min_match=_data.get("min-match"),
                    max_match=_data.get("max-match"),
                ),
            )
        return log_filter

    @staticmethod
    def _get_action(step_name: str, step_data: dict[str, typing.Any]) -> StepAction:
        config_value = step_data.get("action", step_name)
        if config_value in ("install", "warmup"):
            return StepAction.INSTALL
        return StepAction.TESTS


def log_filter_by_odoo_version() -> list[RunbotExcludeWarning]:
    """Returns a list of `RunbotExcludeWarning` objects predefined by odoo version
    This list avoid duplication accross project to filter odoo log warning.

    Returns: The list of `RunbotExcludeWarning` objects for the current odoo version or an empty list

    """
    if importlib.util.find_spec("odoo"):
        return [
            RunbotExcludeWarning(
                name="Default - unaccent not loadable",
                logger="odoo.modules.registry",
                regex=r".*no unaccent\(\) function was found in database.*",
                min_match=0,
                max_match=99,
            ),
        ]

    return []


def warning_filter_by_odoo_version() -> list[RunbotPyWarningsFilter]:
    """Returns a list of `RunbotPyWarningsFilter` objects predefined by odoo version
    This list avoid duplication accross project to filter odoo log warning.

    Returns: The list of `RunbotPyWarningsFilter` objects for the current odoo version or an empty list

    """
    if importlib.util.find_spec("odoo"):
        return [
            RunbotPyWarningsFilter(
                name="[Default] Exclude error in reportlab/pdfbase",
                action="ignore",
                category=SyntaxWarning.__name__,
                message='.*"is" with a literal. Did you mean.*',
            ),
            RunbotPyWarningsFilter(
                name="[Default] Exclude error in vobject/base.py",
                action="ignore",
                category=SyntaxWarning.__name__,
                message=".*invalid escape sequence*",
            ),
        ]

    return []
