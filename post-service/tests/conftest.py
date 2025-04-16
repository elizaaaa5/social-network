import pytest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import PostServiceServicer
from app.database import PostRepository


@pytest.fixture
def mock_post_repository(mocker):
    """Фикстура для мокинга PostRepository."""
    mock = mocker.MagicMock(spec=PostRepository)
    # mock.get_post.return_value = None
    return mock


@pytest.fixture
def post_service_servicer(mock_post_repository):
    """Фикстура для создания экземпляра PostServiceServicer с моком репозитория."""
    servicer = PostServiceServicer()
    servicer.post_repository = mock_post_repository
    return servicer


@pytest.fixture
def mock_grpc_context(mocker):
    """Фикстура для мокинга gRPC контекста."""
    mock_context = mocker.MagicMock()
    mock_context.set_code = mocker.MagicMock()
    mock_context.set_details = mocker.MagicMock()
    return mock_context
