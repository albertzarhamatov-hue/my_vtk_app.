import os
import tempfile
from datetime import datetime
import flet as ft

# Это критически важно для Android!
os.environ["FLET_PYTHON_NO_CTYPES"] = "1"

def get_path():
    # На Android os.getcwd() может быть защищен от записи. 
    # Лучше использовать внутреннюю папку приложения.
    if os.name != 'nt':
        # Путь к внутренней памяти приложения на телефоне
        base = "/storage/emulated/0/Download/Sklad_Set_Data" 
        # Если доступа к общей памяти нет, используем локальную:
        if not os.path.exists("/storage/emulated/0/Download"):
            base = os.path.join(os.getcwd(), "data")
    else:
        base = os.path.join(tempfile.gettempdir(), "Sklad_Set_Final_App")
    
    os.makedirs(base, exist_ok=True)
    return base

BASE_DIR = get_path()

def main(page: ft.Page):
    # Настройка страницы под мобильный экран
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.window_prevent_close = True
    page.scroll = ft.ScrollMode.AUTO # Чтобы всё влезало на экран телефона

    # --- ТВОИ ВЫПАДАЮЩИЕ СПИСКИ С ФИКСОМ ---
    product_drop = ft.Dropdown(
        label="Товар", 
        border_color="#40C4FF",
        alignment=ft.alignment.bottom_center # Чтобы не улетало вверх
    )
    serial_drop = ft.Dropdown(
        label="Серийник / Метраж", 
        border_color="#40C4FF",
        alignment=ft.alignment.bottom_center
    )

    # --- ОСТАЛЬНЫЕ ПОЛЯ ---
    product_in = ft.TextField(label="Название товара")
    count_in = ft.TextField(label="Кол-во")
    
    # Контейнер для вывода логов/ошибок прямо в приложении
    debug_text = ft.Text(size=10, color="grey")

    def navigate(e):
        # Простая смена видимости для теста
        priem_view.visible = not priem_view.visible
        main_menu.visible = not main_menu.visible
        page.update()

    # --- ПРЕДСТАВЛЕНИЯ ---
    main_menu = ft.Column([
        ft.Text("СКЛАД И СЕТЬ", size=28, weight="bold", color="#40C4FF"),
        ft.ElevatedButton("ПРИЕМКА", on_click=navigate, width=300),
        ft.ElevatedButton("СПИСАНИЕ", on_click=lambda _: None, width=300),
        debug_text
    ])

    priem_view = ft.Column([
        ft.IconButton(ft.Icons.ARROW_BACK, on_click=navigate),
        product_in,
        count_in,
        product_drop,
        serial_drop,
        ft.ElevatedButton("СОХРАНИТЬ", bgcolor="#40C4FF", color="black")
    ], visible=False)

    # Выводим путь к базе, чтобы ты видел, куда пишутся файлы
    debug_text.value = f"База данных: {BASE_DIR}"

    page.add(main_menu, priem_view)
    page.update()

# Для сборки APK всегда используем стандартный запуск!
if __name__ == "__main__":
    ft.app(target=main)
