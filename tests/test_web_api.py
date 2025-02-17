import os
import sys
from typing import List

import pytest
from pytest import mark
from fastapi.testclient import TestClient

from namegraph.domains import Domains
from namegraph.generation.categories_generator import Categories
from namegraph.xcollections import CollectionMatcherForAPI, CollectionMatcherForGenerator


@pytest.fixture(scope="module")
def test_test_client():
    Categories.remove_self()
    Domains.remove_self()
    CollectionMatcherForAPI.remove_self()
    CollectionMatcherForGenerator.remove_self()
    os.environ['CONFIG_NAME'] = 'test_config_new'
    # import web_api
    if 'web_api' not in sys.modules:
        import web_api
    else:
        import web_api
        import importlib
        importlib.reload(web_api)
    client = TestClient(web_api.app)
    client.post("/", json={"label": "aaa"})
    return client


def test_read_main(test_test_client):
    client = test_test_client
    response = client.post("/", json={"label": "fire", "metadata": False})

    assert response.status_code == 200

    json = response.json()
    str_names = [name['label'] for name in json]
    assert "discharge" in str_names


@mark.parametrize(
    "name",
    [
        "firepower",
        "dogcat",
        "fire",
        "anarchy"
    ]
)
def test_metadata_scheme(test_test_client, name: str):
    client = test_test_client
    response = client.post("/", json={"label": name})

    assert response.status_code == 200

    json = response.json()

    for generated_name in json:
        assert sorted(generated_name.keys()) == sorted(['label', "tokenized_label", "metadata"])
        assert sorted(generated_name["metadata"].keys()) == sorted([
            'applied_strategies', 'cached_sort_score', 'cached_status',
            'categories', 'interpretation', 'pipeline_name', 'collection_title', 'collection_id', 'grouping_category'
        ])


@mark.parametrize(
    "name, expected_name, expected_strategies",
    [(
            "dogcat",
            "catdog",
            [
                [
                    "PermuteGenerator", "SubnameFilter", "ValidNameFilter"
                ]
            ]
    )]
)
def test_metadata_applied_strategies(test_test_client,
                                     name: str,
                                     expected_name: str,
                                     expected_strategies: List[List[str]]):
    client = test_test_client
    response = client.post("/", json={"label": name})

    assert response.status_code == 200

    json = response.json()
    assert len(json) > 0

    print('==='*20, end='\n\n')
    print(json)
    print('==='*20)

    result = [name for name in json if name['label'] == expected_name]

    assert len(result) == 1

    metadata = result[0]["metadata"]
    assert "applied_strategies" in metadata
    assert len(metadata["applied_strategies"]) == 1

    for strategy in metadata["applied_strategies"]:
        assert strategy in expected_strategies


@mark.parametrize(
    "name",
    [
        "firepower",
        "fire",
        "dogcat",
        "anarchy"
    ]
)
@mark.skip(reason='no count sorter')
def test_count_sorter(test_test_client, name: str):
    client = test_test_client
    response = client.post("/", json={"label": name, "sorter": "count"})

    assert response.status_code == 200

    json = response.json()
    assert len(json) > 0

    scores = [len(gn["metadata"]["applied_strategies"]) for gn in json]
    assert all(first >= second for first, second in zip(scores, scores[1:]))


@mark.parametrize(
    "name",
    [
        "firepower",
        "fire",
        "dogcat",
        "anarchy"
    ]
)
@mark.xfail
def test_length_sorter(test_test_client, name: str):
    client = test_test_client
    response = client.post("/", json={"label": name, "sorter": "length"})

    assert response.status_code == 200

    json = response.json()
    assert len(json) > 0

    lengths = [len(gn['label']) for gn in json]
    assert all([first <= second for first, second in zip(lengths, lengths[1:])])


@mark.parametrize(
    "name, min_suggestions, max_suggestions",
    [
        ("tubeyou", 30, 30),  # testing padding using random pipeline
        ("firepower", 50, 100)
    ]
)
def test_min_max_suggestions_parameters(test_test_client, name: str, min_suggestions: int, max_suggestions: int):
    client = test_test_client
    response = client.post("/", json={
        "label": name,
        "min_suggestions": min_suggestions,
        "max_suggestions": max_suggestions
    })

    assert response.status_code == 200

    json = response.json()
    unique_names = set([suggestion['label'] for suggestion in json])
    assert len(unique_names) == len(json)

    assert min_suggestions <= len(unique_names)
    assert len(unique_names) <= max_suggestions


def test_min_primary_fraction(test_test_client):
    client = test_test_client
    response = client.post("/",
                           json={"label": 'fire', "sorter": "round-robin", "min_primary_fraction": 1.0,
                                 "min_suggestions": 10, "max_suggestions": 10})

    assert response.status_code == 200

    json = response.json()
    assert len(json) > 0
    names = [suggestion['label'] for suggestion in json]
    assert 'iref' not in names


# verifies whether only `RandomAvailableNameGenerator` has been used since it is specified as the only one, which can
# work with an empty input in the test config
def test_empty_input(test_test_client):
    client = test_test_client
    response = client.post("/", json={"label": "",
                                      "min_primary_fraction": 1.0,
                                      "min_suggestions": 100,
                                      "max_suggestions": 100})

    assert response.status_code == 200

    json = response.json()
    assert len(json) > 0

    for name in json:
        applied_strategies = name['metadata']['applied_strategies']
        assert any([
            generator in strategy
            for strategy in applied_strategies
            for generator in ['RandomAvailableNameGenerator']
        ])


def test_no_dots(test_test_client):
    client = test_test_client
    response = client.post("/", json={"label": "there is a . dot"})

    assert response.status_code == 422


@pytest.mark.slow
def test_person_name_generator(test_test_client):
    client = test_test_client
    response = client.post("/",
                           json={"label": "chris", "params": {
                               "country": 'pl'
                           }})

    assert response.status_code == 200

    json = response.json()
    str_names = [name['label'] for name in json]

    assert "iamchris" in str_names
