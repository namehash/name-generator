from generator.app import generate
from hydra import compose, initialize_config_module, initialize

import pytest
from pytest import mark
from typing import List

@mark.parametrize(
    "overrides, expected",
    [
        (["app.query=firepower"], ["fireability", "fireforce", "firemight"]),
    ],
)
def test_basic_generation(overrides: List[str], expected: List[str]) -> None:
    with initialize(version_base=None, config_path="../conf/"):
        cfg = compose(config_name="config", overrides=overrides)
        result = generate(cfg, )
        assert len(set(result).intersection(set(expected))) == len(expected)