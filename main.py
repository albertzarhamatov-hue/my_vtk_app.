import os
import tempfile
from datetime import datetime

# Отключаем ctypes для Android
os.environ["FLET_PYTHON_NO_CTYPES"] = "1"

import flet as ft

# --- ДВИЖОК: НАСТРОЙКА ПУТЕЙ ---
def get_path():
    if os.name != 'nt':
        # Для Android используем локальную папку данных
        base = os.path.join(os.getcwd(), "Sklad_Set_Data")
    else:
        # Для Windows используем временную папку
        base = os.path.join(tempfile.gettempdir(), "Sklad_Set_Final_App")
    
    if not os.path.exists(base): 
        os.makedirs(base, exist_ok=True)
    return base

BASE_DIR = get_path()
STOCK_DIR = os.path.join(BASE_DIR, "stock")
VLAN_DIR = os.path.join(BASE_DIR, "vlan")
IP_DIR = os.path.join(BASE_DIR, "ip_base")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

for d in [STOCK_DIR, VLAN_DIR, IP_DIR, LOGS_DIR]:
    if not os.path.exists(d): 
        os.makedirs(d, exist_ok=True)

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 20
    page.title = "Склад и Сеть"
    page.scroll = "adaptive"

    # Глобальные переменные для настроек
    font_size = 14
    accent_color = "#40C4FF"

    # --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
    def change_font_size(e):
        nonlocal font_size
        font_size = int(e.control.value)
        page.update()

    def change_app_color(color_name):
        page.theme = ft.Theme(color_scheme_seed=color_name)
        page.update()

    # --- ГЛАВНОЕ МЕНЮ ---
    def show_main_menu(e=None):
        page.clean()
        page.add(
            ft.Text("Склад и Сеть", size=24, weight="bold", color=accent_color),
            ft.Divider(height=20, color="transparent"),
            menu_card(ft.Icons.DOWNLOAD, "Приём материала", show_priem),
            menu_card(ft.Icons.PERSON_REMOVE, "Списание на абонента", show_spisanie),
            menu_card(ft.Icons.HISTORY, "История списаний", show_history),
            menu_card(ft.Icons.STORAGE, "База VLAN", show_vlan),
            menu_card(ft.Icons.LANGUAGE, "IP адреса", show_ip),
            menu_card(ft.Icons.SETTINGS, "Настройки", show_settings),
            ft.Divider(height=10, color="transparent"),
            ft.Text("Версия движка: 2.4 ALBERT", color="grey", size=10)
        )

    def menu_card(icon, text, click_func):
        return ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(icon, color=accent_color),
                title=ft.Text(text, size=16),
                on_click=click_func
            ),
            bgcolor="#1C1C1E",
            border_radius=12,
            margin=ft.margin.only(bottom=10)
        )

    # --- ПРИЁМКА ---
    def show_priem(e=None):
        page.clean()
        product_in = ft.TextField(label="Название товара", border_color=accent_color)
        count_in = ft.TextField(label="Кол-во / Метраж", value="1")
        serial_in = ft.TextField(label="S/N (через пробел)", visible=True)
        
        unit_type = ft.SegmentedButton(
            selected={"sn"},
            allow_empty_selection=False,
            on_change=lambda e: setattr(serial_in, "visible", "sn" in e.control.selected) or page.update(),
            segments=[
                ft.Segment(value="sh", label=ft.Text("Шт")),
                ft.Segment(value="m", label=ft.Text("Метры")),
                ft.Segment(value="sn", label=ft.Text("S/N")),
            ],
        )

        priem_results = ft.Column(spacing=10)

        def add_to_stock(e):
            name = product_in.value.strip()
            mode = list(unit_type.selected)[0]
            val = count_in.value.strip()
            if not name or not val: return
            
            ts = datetime.now().strftime('%H%M%S_%f')
            if mode == "sn":
                sns = serial_in.value.strip().split()
                qty = int(val) if val.isdigit() else 1
                for i in range(qty):
                    sn = sns[i] if i < len(sns) else "Б/Н"
                    with open(os.path.join(STOCK_DIR, f"sn_{ts}_{i}.txt"), "w", encoding="utf-8") as f:
                        f.write(f"{name}|{sn}|sn|1")
            else:
                with open(os.path.join(STOCK_DIR, f"{mode}_{ts}.txt"), "w", encoding="utf-8") as f:
                    f.write(f"{name}|{'Метраж' if mode=='m' else 'Штучно'}|{mode}|{val}")
            
            show_priem() # Обновить страницу

        page.add(
            ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=show_main_menu), ft.Text("Приём", size=20)]),
            product_in, unit_type, count_in, serial_in,
            ft.ElevatedButton("ДОБАВИТЬ", on_click=add_to_stock, bgcolor=accent_color, color="black", width=page.width),
            ft.Divider(),
            ft.Text("Текущий склад:"),
            priem_results
        )
        # Загрузка списка
        for f in os.listdir(STOCK_DIR):
            with open(os.path.join(STOCK_DIR, f), "r", encoding="utf-8") as file:
                d = file.read().split("|")
                priem_results.controls.append(ft.Text(f"📦 {d[0]} | {d[1]} | {d[3]}", size=12))
        page.update()

    # --- СПИСАНИЕ ---
    def show_spisanie(e=None):
        page.clean()
        # Загрузка уникальных товаров
        products = set()
        for f in os.listdir(STOCK_DIR):
            with open(os.path.join(STOCK_DIR, f), "r", encoding="utf-8") as file:
                products.add(file.read().split("|")[0])
        
        prod_drop = ft.Dropdown(label="Товар", options=[ft.dropdown.Option(p) for p in products])
        serial_drop = ft.Dropdown(label="Серийник / Партия")
        acc = ft.TextField(label="Лицевой счет")
        addr = ft.TextField(label="Адрес")

        def update_sn(e):
            serial_drop.options = []
            for f in os.listdir(STOCK_DIR):
                with open(os.path.join(STOCK_DIR, f), "r", encoding="utf-8") as file:
                    d = file.read().split("|")
                    if d[0] == prod_drop.value:
                        serial_drop.options.append(ft.dropdown.Option(key=f, text=f"{d[1]} (ост: {d[3]})"))
            page.update()

        prod_drop.on_change = update_sn

        def do_spisanie(e):
            if not serial_drop.value: return
            path = os.path.join(STOCK_DIR, serial_drop.value)
            # Упрощенное удаление (списание полностью)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f: data = f.read().split("|")
                log_entry = f"{datetime.now().strftime('%d.%m %H:%M')} | {data[0]} | SN: {data[1]} | Л/С: {acc.value}"
                with open(os.path.join(LOGS_DIR, "history.txt"), "a", encoding="utf-8") as log:
                    log.write(log_entry + "\n")
                os.remove(path)
            show_main_menu()

        page.add(
            ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=show_main_menu), ft.Text("Списание", size=20)]),
            prod_drop, serial_drop, acc, addr,
            ft.ElevatedButton("ЗАВЕРШИТЬ", on_click=do_spisanie, bgcolor="#FF5252", color="white", width=page.width)
        )

    # --- ИСТОРИЯ ---
    def show_history(e=None):
        page.clean()
        log_view = ft.Column(scroll="adaptive")
        log_path = os.path.join(LOGS_DIR, "history.txt")
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                for line in reversed(f.readlines()):
                    log_view.controls.append(ft.Container(content=ft.Text(line.strip(), size=12), bgcolor="#1C1C1E", padding=10, border_radius=8))
        
        page.add(
            ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=show_main_menu), ft.Text("История")]),
            log_view
        )

    # --- VLAN ---
    def show_vlan(e=None):
        page.clean()
        page.add(
            ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=show_main_menu), ft.Text("База VLAN")]),
            ft.Text("Раздел в разработке", color="grey")
        )

    # --- IP ---
    def show_ip(e=None):
        page.clean()
        page.add(
            ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=show_main_menu), ft.Text("IP Адреса")]),
            ft.Text("Раздел в разработке", color="grey")
        )

    # --- НАСТРОЙКИ ---
    def show_settings(e=None):
        page.clean()
        page.add(
            ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=show_main_menu), ft.Text("Настройки")]),
            ft.Text("Размер шрифта:"),
            ft.Slider(min=10, max=24, value=font_size, on_change=change_font_size),
            ft.Text("Цвет акцента:"),
            ft.Row([
                ft.IconButton(ft.Icons.CIRCLE, icon_color="blue", on_click=lambda _: change_app_color("blue")),
                ft.IconButton(ft.Icons.CIRCLE, icon_color="green", on_click=lambda _: change_app_color("green")),
                ft.IconButton(ft.Icons.CIRCLE, icon_color="red", on_click=lambda _: change_app_color("red")),
            ])
        )

    show_main_menu()

ft.app(target=main)
