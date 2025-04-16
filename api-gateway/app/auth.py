import os
from typing import Dict, Any

import httpx
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

# URL сервиса пользователей (лучше брать из переменных окружения)
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")

# Схема OAuth2 для получения токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


async def validate_token(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Валидирует токен доступа, обращаясь к эндпоинту /me сервиса пользователей.

    Args:
        token: Токен доступа из заголовка Authorization: Bearer.

    Returns:
        Словарь с данными пользователя, если токен валиден.

    Raises:
        HTTPException: Если токен невалиден или сервис пользователей недоступен.
    """
    async with httpx.AsyncClient() as client:
        try:
            print(f"{USER_SERVICE_URL}/me")
            response = await client.get(
                f"{USER_SERVICE_URL}/me", headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()  # Проверяем статус ответа (4xx, 5xx)
        except httpx.RequestError as exc:
            # Ошибка сети или соединения с сервисом пользователей
            raise HTTPException(
                status_code=503, detail=f"User service connection error: {exc}"
            )
        except httpx.HTTPStatusError as exc:
            # Ошибка от сервиса пользователей (например, 401 Unauthorized)
            status_code = exc.response.status_code
            detail = "Invalid token"
            if status_code == 401:
                # Можно попытаться получить детали из ответа сервиса пользователей
                try:
                    error_detail = exc.response.json().get("detail")
                    if error_detail:
                        detail = f"Invalid token: {error_detail}"
                except Exception:
                    pass  # Оставляем detail = "Invalid token"
            elif status_code >= 500:
                detail = f"User service error: Status {status_code}"

            raise HTTPException(status_code=status_code, detail=detail)

    # Если все успешно, возвращаем данные пользователя
    return response.json()
