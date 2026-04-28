import os
import tempfile
from datetime import datetime

# Отключаем ctypes для предотвращения сбоя (Fatal Signal) на Android
os.environ["FLET_PYTHON_NO_CTYPES"] = "1"

import flet as ft

# --- ДВИЖОК: НАСТРОЙКА ПУТЕЙ И ПАПОК ---
def get_path():
    if os.name != 'nt':
        # Путь для Android (текущая папка приложения)
        base = os.path.join(os.getcwd(), "Sklad_Set_Data")
    else:
        # Путь для Windows (временная папка)
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
    page.bgcolor = "#121212"
    page.padding = 20
    page.title = "Склад и Сеть"

    # --- КОМПОНЕНТЫ ИНТЕРФЕЙСА ---
    product_in = ft.TextField(label="Товар", border_color="#40C4FF")
    count_in = ft.TextField(label="Кол-во (напр. 10 или 1000м)", border_color="#40C4FF")
    serial_in = ft.TextField(label="Серийные номера (через пробел)")
    priem_results = ft.Column(spacing=10)

    v_vlan = ft.TextField(label="VLAN", width=100)
    v_ip = ft.TextField(label="IP адрес", width=150)
    v_selo = ft.TextField(label="Село", width=150)
    v_search = ft.TextField(label="Поиск по селу", prefix_icon=ft.Icons.SEARCH)
    vlan_list_display = ft.Column(spacing=10)

    ip_vlan = ft.TextField(label="VLAN", width=100)
    ip_addr = ft.TextField(label="IP адрес", width=150)
    ip_selo = ft.TextField(label="Село", width=150)
    ip_search = ft.TextField(label="Поиск по селу", prefix_icon=ft.Icons.SEARCH)
    ip_list_display = ft.Column(spacing=10)

    product_drop = ft.Dropdown(label="Выбрать товар", border_color="#40C4FF")
    serial_drop = ft.Dropdown(label="Выбрать SN или Метраж", border_color="#40C4FF")
    count_out = ft.TextField(label="Сколько списать (для метров)", value="1")
    account_out = ft.TextField(label="Лицевой счет")
    address_out = ft.TextField(label="Адрес")
    history_list = ft.Column(spacing=10)

    # --- ФУНКЦИИ ДВИЖКА (РАБОТА С ФАЙЛАМИ) ---

    def refresh_all():
        # Обновление списка прихода
        priem_results.controls.clear()
        options = []
        unique_products = set()
        
        if os.path.exists(STOCK_DIR):
            for f in os.listdir(STOCK_DIR):
                with open(os.path.join(STOCK_DIR, f), "r", encoding="utf-8") as file:
                    data = file.read().split("|") # Товар|SN|Тип|Метраж_или_Кол
                    p_name = data[0]
                    unique_products.add(p_name)
                    priem_results.controls.append(
                        ft.Container(
                            content=ft.Text(f"{p_name} | {data[1]} | {data[3]}", size=14),
                            bgcolor="#1E1E20", padding=10, border_radius=8
                        )
                    )
        product_drop.options = [ft.dropdown.Option(p) for p in unique_products]
        update_vlan_list()
        update_ip_list()
        page.update()

    def add_to_stock(e):
        name = product_in.value.strip()
        raw_count = count_in.value.strip().lower()
        sns = serial_in.value.strip().split()
        
        if name and raw_count:
            if "м" in raw_count or "m" in raw_count:
                val = raw_count.replace("м","").replace("m","")
                fname = f"m_{datetime.now().strftime('%H%M%S_%f')}.txt"
                with open(os.path.join(STOCK_DIR, fname), "w", encoding="utf-8") as f:
                    f.write(f"{name}|Метраж|m|{val}")
            else:
                qty = int(raw_count) if raw_count.isdigit() else 1
                for i in range(qty):
                    sn = sns[i] if i < len(sns) else "Б/Н"
                    fname = f"sn_{datetime.now().strftime('%H%M%S_%f')}.txt"
                    with open(os.path.join(STOCK_DIR, fname), "w", encoding="utf-8") as f:
                        f.write(f"{name}|{sn}|sn|1")
            
            product_in.value = ""; count_in.value = ""; serial_in.value = ""
            refresh_all()

    def add_vlan(e):
        if v_vlan.value and v_selo.value:
            fname = f"v_{datetime.now().strftime('%H%M%S_%f')}.txt"
            content = f"{v_selo.value}|{v_vlan.value}|{v_ip.value}"
            with open(os.path.join(VLAN_DIR, fname), "w", encoding="utf-8") as f:
                f.write(content)
            v_vlan.value = ""; v_ip.value = ""; v_selo.value = ""
            update_vlan_list()

    def update_vlan_list(e=None):
        vlan_list_display.controls.clear()
        search = v_search.value.lower() if v_search.value else ""
        if os.path.exists(VLAN_DIR):
            for f in os.listdir(VLAN_DIR):
                with open(os.path.join(VLAN_DIR, f), "r", encoding="utf-8") as file:
                    data = file.read().split("|")
                    if search in data[0].lower():
                        vlan_list_display.controls.append(
                            ft.Container(
                                content=ft.Row([
                                    ft.Column([ft.Text(data[0], weight="bold"), ft.Text(f"VLAN: {data[1]} | IP: {data[2]}", color="grey")], expand=True),
                                    ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda _, path=f: [os.remove(os.path.join(VLAN_DIR, path)), update_vlan_list()])
                                ]), bgcolor="#1E1E20", padding=10, border_radius=10
                            )
                        )
        page.update()

    def add_ip(e):
        if ip_addr.value and ip_selo.value:
            fname = f"ip_{datetime.now().strftime('%H%M%S_%f')}.txt"
            content = f"{ip_selo.value}|{ip_addr.value}|{ip_vlan.value}"
            with open(os.path.join(IP_DIR, fname), "w", encoding="utf-8") as f:
                f.write(content)
            ip_vlan.value = ""; ip_addr.value = ""; ip_selo.value = ""
            update_ip_list()

    def update_ip_list(e=None):
        ip_list_display.controls.clear()
        search = ip_search.value.lower() if ip_search.value else ""
        for f in os.listdir(IP_DIR):
            with open(os.path.join(IP_DIR, f), "r", encoding="utf-8") as file:
                data = file.read().split("|")
                if search in data[0].lower():
                    ip_list_display.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Column([ft.Text(data[0], weight="bold"), ft.Text(f"IP: {data[1]} | VLAN: {data[2]}", color="grey")], expand=True),
                                ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda _, path=f: [os.remove(os.path.join(IP_DIR, path)), update_ip_list()])
                            ]), bgcolor="#1E1E20", padding=10, border_radius=10
                        )
                    )
        page.update()

    # --- НАВИГАЦИЯ ---
    def navigate(view):
        main_view.visible = (view == "main")
        priem_view.visible = (view == "priem")
        spisanie_view.visible = (view == "spisanie")
        history_view.visible = (view == "history")
        vlan_view.visible = (view == "vlan")
        ip_view.visible = (view == "ip")
        settings_view.visible = (view == "settings")
        page.update()

    def menu_card(icon, text, view_name):
        return ft.Container(
            content=ft.ListTile(leading=ft.Icon(icon, color="#40C4FF"), title=ft.Text(text), on_click=lambda _: navigate(view_name)),
            bgcolor="#1E1E20", border_radius=12, margin=8
        )

    # --- ПРЕДСТАВЛЕНИЯ (Твой дизайн) ---
    main_view = ft.Column([
        ft.Text("Склад и Сеть", size=24, weight="bold", color="#40C4FF"),
        menu_card(ft.Icons.DOWNLOAD, "Приём материала", "priem"),
        menu_card(ft.Icons.PERSON_REMOVE, "Списание на абонента", "spisanie"),
        menu_card(ft.Icons.HISTORY, "История", "history"),
        menu_card(ft.Icons.STORAGE, "База VLAN", "vlan"),
        menu_card(ft.Icons.LANGUAGE, "IP адреса", "ip"),
        menu_card(ft.Icons.SETTINGS, "Настройки", "settings"),
    ])

    priem_view = ft.Column([
        ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: navigate("main")), ft.Text("Приём")]),
        product_in, count_in, serial_in,
        ft.ElevatedButton("ДОБАВИТЬ", on_click=add_to_stock, bgcolor="#40C4FF", color="black", width=500),
        priem_results
    ], visible=False, scroll=ft.ScrollMode.AUTO)

    # Оставим заглушки для остальных вью, логика там аналогична - чтение файлов из папок
    spisanie_view = ft.Column([
        ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: navigate("main")), ft.Text("Списание")]),
        product_drop, serial_drop, count_out, account_out, address_out,
        ft.ElevatedButton("ЗАВЕРШИТЬ", bgcolor="#FF5252", color="white", width=500),
    ], visible=False)

    history_view = ft.Column([
        ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: navigate("main")), ft.Text("История")]),
        history_list
    ], visible=False, scroll=ft.ScrollMode.AUTO)

    vlan_view = ft.Column([
        ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: navigate("main")), ft.Text("База VLAN")]),
        ft.Row([v_vlan, v_ip, v_selo]),
        ft.ElevatedButton("ДОБАВИТЬ В БАЗУ", on_click=add_vlan, bgcolor="#40C4FF", color="black", width=500),
        ft.Divider(),
        v_search,
        vlan_list_display
    ], visible=False, scroll=ft.ScrollMode.AUTO)

    ip_view = ft.Column([
        ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: navigate("main")), ft.Text("База IP")]),
        ft.Row([ip_vlan, ip_addr, ip_selo]),
        ft.ElevatedButton("ДОБАВИТЬ IP", on_click=add_ip, bgcolor="#40C4FF", color="black", width=500),
        ft.Divider(),
        ip_search,
        ip_list_display
    ], visible=False, scroll=ft.ScrollMode.AUTO)

    settings_view = ft.Column([
        ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: navigate("main")), ft.Text("Настройки")]),
        ft.Text("Версия движка: 2.0 (Файловая система)")
    ], visible=False)

    v_search.on_change = update_vlan_list
    ip_search.on_change = update_ip_list

    page.add(main_view, priem_view, spisanie_view, history_view, vlan_view, ip_view, settings_view)
    refresh_all()

ft.app(target=main)
