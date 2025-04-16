import pytest
import uuid
from datetime import datetime, timezone
import grpc

# Импортируем необходимые классы и proto
from app.main import PostServiceServicer
from app.database import Post # Импортируем модель Post для создания тестовых данных
from app.proto import post_service_pb2

# Используем фикстуры из conftest.py
# pytest автоматически обнаружит post_service_servicer, mock_post_repository, mock_grpc_context

def test_create_post(post_service_servicer, mock_post_repository, mock_grpc_context):
    user_id = str(uuid.uuid4())
    title = "Test Title"
    content = "Test Content"
    post_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    # Настраиваем мок репозитория
    mock_post = Post(
        id=post_id,
        user_id=user_id,
        title=title,
        content=content,
        created_at=now,
        updated_at=now
    )
    mock_post_repository.create_post.return_value = mock_post

    # Создаем запрос
    request = post_service_pb2.CreatePostRequest(
        user_id=user_id, title=title, content=content
    )

    # Вызываем метод сервиса
    response = post_service_servicer.CreatePost(request, mock_grpc_context)

    # Проверяем, что метод репозитория был вызван с правильными аргументами
    mock_post_repository.create_post.assert_called_once_with(
        user_id=user_id, title=title, content=content
    )

    # Проверяем ответ
    assert response.id == str(post_id)
    assert response.user_id == user_id
    assert response.title == title
    assert response.content == content
    assert response.created_at == now.isoformat()
    assert response.updated_at == now.isoformat()
    mock_grpc_context.set_code.assert_not_called() # Убедимся, что ошибки не было

def test_get_post_success(post_service_servicer, mock_post_repository, mock_grpc_context):
    post_id = uuid.uuid4()
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    mock_post = Post(
        id=post_id,
        user_id=user_id,
        title="Existing Post",
        content="Content",
        created_at=now,
        updated_at=now
    )
    mock_post_repository.get_post.return_value = mock_post

    request = post_service_pb2.GetPostRequest(post_id=str(post_id))
    response = post_service_servicer.GetPost(request, mock_grpc_context)

    mock_post_repository.get_post.assert_called_once_with(str(post_id))
    assert response.id == str(post_id)
    assert response.user_id == user_id
    mock_grpc_context.set_code.assert_not_called()

def test_get_post_not_found(post_service_servicer, mock_post_repository, mock_grpc_context):
    post_id = str(uuid.uuid4())
    mock_post_repository.get_post.return_value = None # Пост не найден

    request = post_service_pb2.GetPostRequest(post_id=post_id)
    response = post_service_servicer.GetPost(request, mock_grpc_context)

    mock_post_repository.get_post.assert_called_once_with(post_id)
    mock_grpc_context.set_code.assert_called_once_with(grpc.StatusCode.NOT_FOUND)
    mock_grpc_context.set_details.assert_called_once()
    # Проверяем, что возвращается пустой Post объект в случае ошибки
    assert response == post_service_pb2.Post()


def test_list_posts(post_service_servicer, mock_post_repository, mock_grpc_context):
    user_id = str(uuid.uuid4())
    page = 1
    page_size = 5
    now = datetime.now(timezone.utc)
    mock_posts = [
        Post(id=uuid.uuid4(), user_id=user_id, title=f"Post {i}", content="Content", created_at=now, updated_at=now)
        for i in range(page_size)
    ]
    total_posts = 15
    mock_post_repository.list_posts.return_value = (mock_posts, total_posts)

    request = post_service_pb2.ListPostsRequest(
        user_id=user_id, page=page, page_size=page_size
    )
    response = post_service_servicer.ListPosts(request, mock_grpc_context)

    mock_post_repository.list_posts.assert_called_once_with(
        user_id=user_id, page=page, page_size=page_size
    )
    assert response.total == total_posts
    assert len(response.posts) == page_size
    assert response.posts[0].id == str(mock_posts[0].id)
    assert response.posts[0].user_id == user_id
    mock_grpc_context.set_code.assert_not_called()


def test_update_post_success(post_service_servicer, mock_post_repository, mock_grpc_context):
    post_id = uuid.uuid4()
    user_id = str(uuid.uuid4())
    updated_title = "Updated Title"
    updated_content = "Updated Content"
    now = datetime.now(timezone.utc)
    updated_time = datetime.now(timezone.utc)

    mock_updated_post = Post(
        id=post_id,
        user_id=user_id, # user_id не меняется при обновлении
        title=updated_title,
        content=updated_content,
        created_at=now, # created_at не меняется
        updated_at=updated_time
    )
    mock_post_repository.update_post.return_value = mock_updated_post

    request = post_service_pb2.UpdatePostRequest(
        post_id=str(post_id), title=updated_title, content=updated_content
    )
    response = post_service_servicer.UpdatePost(request, mock_grpc_context)

    mock_post_repository.update_post.assert_called_once_with(
        post_id=str(post_id), title=updated_title, content=updated_content
    )
    assert response.id == str(post_id)
    assert response.title == updated_title
    assert response.content == updated_content
    assert response.updated_at == updated_time.isoformat()
    mock_grpc_context.set_code.assert_not_called()

def test_update_post_not_found(post_service_servicer, mock_post_repository, mock_grpc_context):
    post_id = str(uuid.uuid4())
    mock_post_repository.update_post.return_value = None # Пост не найден для обновления

    request = post_service_pb2.UpdatePostRequest(
        post_id=post_id, title="Any", content="Any"
    )
    response = post_service_servicer.UpdatePost(request, mock_grpc_context)

    mock_post_repository.update_post.assert_called_once_with(
        post_id=post_id, title="Any", content="Any"
    )
    mock_grpc_context.set_code.assert_called_once_with(grpc.StatusCode.NOT_FOUND)
    mock_grpc_context.set_details.assert_called_once()
    assert response == post_service_pb2.Post()


def test_delete_post_success(post_service_servicer, mock_post_repository, mock_grpc_context):
    post_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    mock_post_repository.delete_post.return_value = True # Успешное удаление

    request = post_service_pb2.DeletePostRequest(post_id=post_id, user_id=user_id)
    response = post_service_servicer.DeletePost(request, mock_grpc_context)

    mock_post_repository.delete_post.assert_called_once_with(
        post_id=post_id, user_id=user_id
    )
    assert response.success is True
    mock_grpc_context.set_code.assert_not_called()

def test_delete_post_not_found_or_unauthorized(post_service_servicer, mock_post_repository, mock_grpc_context):
    post_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    mock_post_repository.delete_post.return_value = False # Неудачное удаление (не найден или не авторизован)

    request = post_service_pb2.DeletePostRequest(post_id=post_id, user_id=user_id)
    response = post_service_servicer.DeletePost(request, mock_grpc_context)

    mock_post_repository.delete_post.assert_called_once_with(
        post_id=post_id, user_id=user_id
    )
    assert response.success is False
    mock_grpc_context.set_code.assert_called_once_with(grpc.StatusCode.NOT_FOUND)
    mock_grpc_context.set_details.assert_called_once()
