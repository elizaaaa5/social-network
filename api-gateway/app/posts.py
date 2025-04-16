import os
import uuid
from typing import List, Optional, Dict, Any

import grpc
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

# Импортируем сгенерированный код
from app.proto import post_service_pb2, post_service_pb2_grpc

# Импортируем функцию валидации токена из модуля auth
from app.auth import validate_token

# Адрес сервиса постов (лучше брать из переменных окружения)
POST_SERVICE_URL = os.getenv("POST_SERVICE_URL", "post-service:50051")

router = APIRouter(prefix="/api/v1/posts", tags=["posts"])


# --- Pydantic модели для запросов и ответов ---
class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=1)


class PostResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    content: str
    created_at: str
    updated_at: str


class ListPostsResponse(BaseModel):
    posts: List[PostResponse]
    total: int


# --- Функция для получения gRPC стаба ---
def get_post_service_stub():
    # TODO: Рассмотреть возможность переиспользования канала (channel)
    # для повышения производительности, например, с помощью Depends или middleware.
    try:
        channel = grpc.insecure_channel(POST_SERVICE_URL)
        stub = post_service_pb2_grpc.PostServiceStub(channel)
        yield stub
    except grpc.RpcError as e:
        # Логирование ошибки может быть полезно здесь
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Post service connection error: {e.details()}",
        )
    finally:
        if "channel" in locals() and channel:
            channel.close()


# --- Обработчики ошибок gRPC ---
def handle_grpc_error(e: grpc.RpcError):
    if e.code() == grpc.StatusCode.NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.details())
    elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.details())
    elif (
        e.code() == grpc.StatusCode.PERMISSION_DENIED
    ):  # Или UNAUTHENTICATED в зависимости от логики сервиса
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.details())
    else:
        # Общая ошибка сервера для других gRPC ошибок
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Post service error: {e.details()}",
        )


# --- Эндпоинты ---
@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    user_data: Dict[str, Any] = Depends(validate_token),
    stub: post_service_pb2_grpc.PostServiceStub = Depends(get_post_service_stub),
):
    user_id = user_data.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token data"
        )

    request = post_service_pb2.CreatePostRequest(
        user_id=str(user_id), title=post_data.title, content=post_data.content
    )
    try:
        response = stub.CreatePost(request)
        return PostResponse(
            id=uuid.UUID(response.id),
            user_id=uuid.UUID(response.user_id),
            title=response.title,
            content=response.content,
            created_at=response.created_at,
            updated_at=response.updated_at,
        )
    except grpc.RpcError as e:
        handle_grpc_error(e)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: uuid.UUID,
    stub: post_service_pb2_grpc.PostServiceStub = Depends(get_post_service_stub),
    # Для получения поста не требуется авторизация по ТЗ, но можно добавить user_data: Dict[str, Any] = Depends(validate_token) если нужно
):
    request = post_service_pb2.GetPostRequest(post_id=str(post_id))
    try:
        response = stub.GetPost(request)
        return PostResponse(
            id=uuid.UUID(response.id),
            user_id=uuid.UUID(response.user_id),
            title=response.title,
            content=response.content,
            created_at=response.created_at,
            updated_at=response.updated_at,
        )
    except grpc.RpcError as e:
        handle_grpc_error(e)


@router.get("/", response_model=ListPostsResponse)
async def list_posts(
    user_id: uuid.UUID,  # Фильтрация по user_id обязательна
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    stub: post_service_pb2_grpc.PostServiceStub = Depends(get_post_service_stub),
    # Авторизация не требуется для просмотра постов пользователя по ТЗ
):
    request = post_service_pb2.ListPostsRequest(
        user_id=str(user_id), page=page, page_size=page_size
    )
    try:
        response = stub.ListPosts(request)
        posts_list = [
            PostResponse(
                id=uuid.UUID(p.id),
                user_id=uuid.UUID(p.user_id),
                title=p.title,
                content=p.content,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in response.posts
        ]
        return ListPostsResponse(posts=posts_list, total=response.total)
    except grpc.RpcError as e:
        handle_grpc_error(e)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: uuid.UUID,
    post_data: PostUpdate,
    user_data: Dict[str, Any] = Depends(validate_token),
    stub: post_service_pb2_grpc.PostServiceStub = Depends(get_post_service_stub),
):
    # Проверяем, что пользователь обновляет свой пост (хотя сервис постов должен это делать сам)
    # user_id = user_data.get("id")
    # if not user_id:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token data")
    # TODO: Возможно, стоит добавить проверку в гейтвее, что user_id из токена совпадает с user_id поста перед отправкой запроса

    update_data = post_data.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update"
        )

    request = post_service_pb2.UpdatePostRequest(post_id=str(post_id), **update_data)
    try:
        response = stub.UpdatePost(request)
        return PostResponse(
            id=uuid.UUID(response.id),
            user_id=uuid.UUID(response.user_id),
            title=response.title,
            content=response.content,
            created_at=response.created_at,
            updated_at=response.updated_at,
        )
    except grpc.RpcError as e:
        handle_grpc_error(e)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: uuid.UUID,
    user_data: Dict[str, Any] = Depends(validate_token),
    stub: post_service_pb2_grpc.PostServiceStub = Depends(get_post_service_stub),
):
    user_id = user_data.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token data"
        )

    request = post_service_pb2.DeletePostRequest(
        post_id=str(post_id), user_id=str(user_id)
    )
    try:
        response = stub.DeletePost(request)
        if not response.success:
            # Эта ситуация не должна возникать, если handle_grpc_error работает правильно,
            # но добавим для надежности.
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found or not authorized",
            )
        # Возвращаем пустой ответ с кодом 204
        return None
    except grpc.RpcError as e:
        # NOT_FOUND или PERMISSION_DENIED должны быть обработаны здесь
        handle_grpc_error(e)
