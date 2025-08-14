from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd


def export_to_excel(
    data: List[Union[Any, Dict[str, Any]]], file_path: Optional[str] = None
) -> str:
    """
    Экспортирует данные в Excel файл.

    Args:
        data: Список объектов SQLAlchemy или словарей с данными
        file_path: Путь к файлу (если не указан, создается автоматически)

    Returns:
        str: Путь к созданному файлу
    """
    if not data:
        raise ValueError("Список данных пуст")

    if file_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exports_dir = Path("exports")
        exports_dir.mkdir(exist_ok=True)
        file_path = exports_dir / f"export_{timestamp}.xlsx"
    else:
        file_path = Path(file_path)
        if file_path.suffix.lower() not in ['.xlsx', '.xls']:
            file_path = file_path.with_suffix('.xlsx')
        file_path.parent.mkdir(parents=True, exist_ok=True)

    # Конвертируем данные в список словарей
    records = []
    for item in data:
        if isinstance(item, dict):
            records.append(item)
        else:
            # Конвертируем SQLAlchemy объект в словарь
            record = {}
            for column in item.__table__.columns:
                value = getattr(item, column.name)
                # Форматируем timestamp поля
                if column.name.endswith("_date") and isinstance(value, int):
                    try:
                        value = datetime.fromtimestamp(value).strftime(
                            "%d.%m.%Y %H:%M:%S"
                        )
                    except (ValueError, OSError):
                        pass
                record[column.name] = value
            records.append(record)

    # Создаем DataFrame и экспортируем в Excel
    df = pd.DataFrame(records)
    df = df.fillna("")

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

        # Автоматическая настройка ширины колонок
        worksheet = writer.book.active
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    return str(file_path)
