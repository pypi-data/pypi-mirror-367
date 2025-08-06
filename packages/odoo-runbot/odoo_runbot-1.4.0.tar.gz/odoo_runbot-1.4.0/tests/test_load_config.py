import pathlib

from odoo_runbot import runbot_env
from odoo_runbot.runbot_env import RunbotExcludeWarning, RunbotStepConfig, RunbotToolConfig, StepAction


def sample_config(fname: str) -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent.joinpath("sample_config", fname)


def test_minimal_config():
    """[tool.runbot]
    modules = ["module_to_test"]
    """
    config_path = sample_config("pyproject_minimal.toml")
    config = runbot_env.RunbotToolConfig.load_from_toml(config_path)
    global_module = ["module_to_test"]
    assert config == RunbotToolConfig(
        include_current_project=True,
        steps=[
            RunbotStepConfig(
                name="default",
                modules=global_module,
                action=StepAction.TESTS,
                test_tags=[],
                coverage=True,
                log_filters=[],
            ),
        ],
        pretty=True,
    )


def test_pyproject_classic():
    global_module = ["module_to_test", "module_to_test_2"]
    global_log_filter = [
        RunbotExcludeWarning(
            name="All Steps - Logger Filter 1",
            regex=".*log to accept.*",
            logger="",
            min_match=1,
            max_match=1,
        )
    ]

    config = runbot_env.RunbotToolConfig.load_from_toml(sample_config("pyproject_classic.toml"))
    config_full = runbot_env.RunbotToolConfig.load_from_toml(sample_config("pyproject_classic.full.toml"))
    assert (
        config
        == config_full
        == RunbotToolConfig(
            include_current_project=True,
            steps=[
                RunbotStepConfig(
                    name="install",
                    modules=global_module,
                    action=StepAction.INSTALL,
                    test_tags=[],
                    coverage=False,
                    log_filters=global_log_filter,
                ),
                RunbotStepConfig(
                    name="run-test",
                    modules=global_module,
                    action=StepAction.TESTS,
                    test_tags=["/module_to_test:MyTestCase", "/module_to_test"],
                    coverage=True,
                    log_filters=global_log_filter,
                ),
            ],
            pretty=True,
        )
    )


def test_pyproject_complex():
    config = runbot_env.RunbotToolConfig.load_from_toml(sample_config("pyproject_complex.toml"))

    global_regex = [
        runbot_env.RunbotExcludeWarning(
            name="All Steps - Logger Filter 1",
            regex=r".*global-regex-warning-1.*",
        ),
        runbot_env.RunbotExcludeWarning(
            name="global-regex-warning-2",
            regex=r".*global-regex-warning-2.*",
            min_match=1,
            max_match=2,
        ),
    ]
    global_module = ["module_to_test", "module_to_test2"]
    global_coverage = False

    assert config == RunbotToolConfig(
        include_current_project=True,
        steps=[
            RunbotStepConfig(
                name="install",
                modules=["first_module_to_install"],
                action=StepAction.INSTALL,
                test_tags=[],
                coverage=global_coverage,
                log_filters=[
                    *global_regex,
                    RunbotExcludeWarning(
                        regex=".*Install filter.*",
                        name="Step install - Logger Filter 3",
                        min_match=1,
                        max_match=1,
                    ),
                ],
            ),
            RunbotStepConfig(
                name="tests",
                modules=global_module,
                action=StepAction.TESTS,
                test_tags=["+at-install", "-post-install"],
                coverage=True,
                log_filters=[
                    *global_regex,
                    RunbotExcludeWarning(
                        regex=".*regex warning.*",
                        name="test-regex-log-warning-2",
                        min_match=1,
                        max_match=1,
                    ),
                ],
            ),
            RunbotStepConfig(
                name="warmup",
                modules=["second_module_to_install"],
                action=StepAction.INSTALL,
                test_tags=[],
                coverage=global_coverage,
                log_filters=global_regex,
            ),
            RunbotStepConfig(
                name="Post install test",
                modules=["module_to_test2"],
                action=StepAction.TESTS,
                test_tags=["-at-install", "+post-install"],
                coverage=False,
                log_filters=[
                    *global_regex,
                    RunbotExcludeWarning(
                        name="Step Post install test - Logger Filter 3",
                        regex=".*Post install test regex-warnings.*",
                        min_match=2,
                        max_match=2,
                    ),
                ],
            ),
        ],
        pretty=True,
    )


def test_min_max_match_log_filter():
    assert RunbotExcludeWarning(name="A", regex="A", min_match=2) == RunbotExcludeWarning(
        name="A",
        regex="A",
        min_match=2,
        max_match=2,
    ), "Assert Min and max match follow each other if not set"
    assert RunbotExcludeWarning(name="A", regex="A", min_match=10, max_match=2) == RunbotExcludeWarning(
        name="A",
        regex="A",
        max_match=10,
        min_match=10,
    ), "Assert Min and max match follow each other if not set"
    assert RunbotExcludeWarning(name="A", regex="A", min_match=-1) == RunbotExcludeWarning(
        name="A",
        regex="A",
        max_match=1,
        min_match=0,
    ), "Assert if Min is -1 then this means 0 min match"
    assert RunbotExcludeWarning(name="A", regex="A", min_match=0) == RunbotExcludeWarning(
        name="A",
        regex="A",
        max_match=1,
        min_match=0,
    ), "Assert if Min is 0 then this means 0 min match"
    assert RunbotExcludeWarning(name="A", regex="A", max_match=0) == RunbotExcludeWarning(
        name="A",
        regex="A",
        max_match=0,
        min_match=0,
    ), "Assert if Max is 0 means exacly 0 match possible"
    assert RunbotExcludeWarning(name="A", regex="A", max_match=999) == RunbotExcludeWarning(
        name="A",
        regex="A",
        max_match=100,
        min_match=1,
    ), "Assert if Max can't be more than 100If you want more than 100, you should fix this logger :-)"
