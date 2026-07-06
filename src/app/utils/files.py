import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import UPLOAD_DIR

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}
SAFE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 200 * 1024


async def process_and_save_photo(photo: UploadFile) -> str:
    """Обрабатывает и сохраняет загруженную фотографию.

    Проверяет тип файла (только JPG/PNG) и размер (макс. 200 КБ).
    Генерирует уникальное имя файла для предотвращения коллизий.

    Args:
        photo: Объект UploadFile с фотографией.

    Returns:
        str: Имя сохранённого файла.

    Raises:
        HTTPException: 400 при неподдерживаемом формате или превышении размера.
    """
    if photo.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(400, detail="Разрешены только изображения JPG или PNG")

    contents = await photo.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            400, detail=f"Файл слишком большой. Максимум {MAX_FILE_SIZE // 1024} КБ"
        )

    original_ext = Path(photo.filename).suffix.lower() if photo.filename else ""

    if original_ext not in SAFE_EXTENSIONS:
        ext = ".png" if photo.content_type == "image/png" else ".jpg"
    else:
        ext = original_ext

    new_filename = f"{uuid.uuid4()}{ext}"

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    save_path = UPLOAD_DIR / new_filename

    with open(save_path, "wb") as f:
        f.write(contents)

    return new_filename


def delete_photo(filename: str) -> None:
    """Удаляет файл фотографии с диска, если он существует.

    Args:
        filename: Имя файла для удаления.
    """
    file_path = UPLOAD_DIR / filename
    if file_path.exists():
        file_path.unlink()
