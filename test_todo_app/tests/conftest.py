import pytest
from typing import Tuple
from fasthtml.common import Client, Table
from todos import create_app

@pytest.fixture
def test_client_and_database() -> Tuple[Client, Table]:
    """test_client_and_database will be available to all test functions in the project"""
    app, todos = create_app(mode="test")
    return Client(app=app), todos
