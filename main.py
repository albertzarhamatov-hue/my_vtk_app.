import os
import tempfile
from datetime import datetime

# Отключаем ctypes для предотвращения сбоя на Android
os.environ["FLET_PYTHON_NO_CTYPES"] = "1"

import flet as ft

# --- ТВОЙ ДВИЖОК: НАСТРОЙКА ПУТЕЙ ---
def get_path():
    if os.name != 'nt':
        base = os.path.join(os.getcwd(), "Sklad_Set_Data")
    else:
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

    # --- ЭЛЕМЕНТЫ ИНТЕРФЕЙСА ---
    product_in = ft.TextField(label="Товар", border_color="#40C4FF")
    count_in = ft.TextField(label="Кол-во (напр. 10 или 1000м)", border_color="#40C4FF")
    serial_in = ft.TextField(label="Серийные номера (через пробел)")
    priem_results = ft.Column(spacing=10)

    # Добавлена настройка alignment, чтобы меню открывалось вниз/ровно
    product_drop = ft.Dropdown(
        label="Выбрать товар", 
        border_color="#40C4FF",
        alignment=ft.alignment.bottom_center 
    )
    serial_drop = ft.Dropdown(
        label="Выбрать SN или Метраж", 
        border_color="#40C4FF",
        alignment=ft.alignment.bottom_center
    )
    
    count_out = ft.TextField(label="Сколько списать", value="1")
    account_out = ft.TextField(label="Лицевой счет")
    address_out = ft.TextField(label="Адрес")
    history_list = ft.Column(spacing=10)

    # Остальные поля
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

    # --- ТВОИ ФУНКЦИИ ---
    def update_history_list():
        history_list.controls.clear()
        if os.path.exists(LOGS_DIR):
            files = sorted(os.listdir(LOGS_DIR), reverse=True)
            for f in files:
                with open(os.path.join(LOGS_DIR, f), "r", encoding="utf-8") as file:
                    content = file.read()
                    history_list.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Text(content, size=12, expand=True),
                                ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color="red700", icon_size=18,
                                             on_click=lambda _, p=f: [os.remove(os.path.join(LOGS_DIR, p)), update_history_list()])
                            ]),
                            bgcolor="#1E1E20", padding=10, border_radius=10
                        )
                    )
        page.update()

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
                                    ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda _, p=f: [os.remove(os.path.join(VLAN_DIR, p)), update_vlan_list()])
                                ]), bgcolor="#1E1E20", padding=10, border_radius=10
                            )
                        )
        page.update()

    def update_ip_list(e=None):
        ip_list_display.controls.clear()
        search = ip_search.value.lower() if ip_search.value else ""
        if os.path.exists(IP_DIR):
            for f in os.listdir(IP_DIR):
                with open(os.path.join(IP_DIR, f), "r", encoding="utf-8") as file:
                    data = file.read().split("|")
                    if search in data[0].lower():
                        ip_list_display.controls.append(
                            ft.Container(
                                content=ft.Row([
                                    ft.Column([ft.Text(data[0], weight="bold"), ft.Text(f"IP: {data[1]} | VLAN: {data[2]}", color="grey")], expand=True),
                                    ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda _, p=f: [os.remove(os.path.join(IP_DIR, p)), update_ip_list()])
                                ]), bgcolor="#1E1E20", padding=10, border_radius=10
                            )
                        )
        page.update()

    def refresh_all():
        priem_results.controls.clear()
        unique_products = set()
        if os.path.exists(STOCK_DIR):
            for f in os.listdir(STOCK_DIR):
                with open(os.path.join(STOCK_DIR, f), "r", encoding="utf-8") as file:
                    data = file.read().split("|")
                    unique_products.add(data[0])
                    priem_results.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Text(f"{data[0]} | {data[1]} | {data[3]}", size=14, expand=True),
                                ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color="red400", icon_size=18,
                                             on_click=lambda _, p=f: [os.remove(os.path.join(STOCK_DIR, p)), refresh_all()])
                            ]),
                            bgcolor="#1E1E20", padding=10, border_radius=8
                        )
                    )
        product_drop.options = [ft.dropdown.Option(p) for p in sorted(list(unique_products))]
        update_vlan_list()
        update_ip_list()
        update_history_list()

    # --- ЛОГИКА ---
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

    def update_serials(e):
        selected_prod = product_drop.value
        serial_drop.options = []
        if selected_prod and os.path.exists(STOCK_DIR):
            for f in os.listdir(STOCK_DIR):
                with open(os.path.join(STOCK_DIR, f), "r", encoding="utf-8") as file:
                    data = file.read().split("|")
                    if data[0] == selected_prod:
                        serial_drop.options.append(ft.dropdown.Option(key=f, text=f"{data[1]} ({data[3]})"))
        page.update()

    product_drop.on_change = update_serials

    def complete_spisanie(e):
        if not product_drop.value or not serial_drop.value: return
        file_path = os.path.join(STOCK_DIR, serial_drop.value)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = f.read().split("|")
            prod_name, sn_val, mode, current_qty = data[0], data[1], data[2], float(data[3])
            minus_qty = float(count_out.value.replace(",", ".")) if count_out.value else 1.0
            
            if mode == "m":
                new_qty = current_qty - minus_qty
                if new_qty <= 0:
                    os.remove(file_path)
                    final_info = f"{current_qty} м (полн.)"
                else:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(f"{prod_name}|{sn_val}|{mode}|{new_qty}")
                    final_info = f"{minus_qty} м (ост. {new_qty})"
            else:
                os.remove(file_path)
                final_info = f"SN: {sn_val}"

            log_name = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.txt"
            log_text = f"{datetime.now().strftime('%d.%m %H:%M')} | {prod_name} | {final_info} | Л/С: {account_out.value} | Адр: {address_out.value}"
            with open(os.path.join(LOGS_DIR, log_name), "w", encoding="utf-8") as f:
                f.write(log_text)
            
            account_out.value = ""; address_out.value = ""; count_out.value = "1"
            refresh_all()
            navigate("history")

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

    # --- ПРЕДСТАВЛЕНИЯ ---
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

    spisanie_view = ft.Column([
        ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: navigate("main")), ft.Text("Списание")]),
        product_drop, serial_drop, count_out, account_out, address_out,
        ft.ElevatedButton("ЗАВЕРШИТЬ", on_click=complete_spisanie, bgcolor="#FF5252", color="white", width=500),
    ], visible=False, scroll=ft.ScrollMode.AUTO)

    history_view = ft.Column([
        ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: navigate("main")), ft.Text("История")]),
        history_list
    ], visible=False, scroll=ft.ScrollMode.AUTO)

    vlan_view = ft.Column([
        ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: navigate("main")), ft.Text("База VLAN")]),
        ft.Row([v_vlan, v_ip, v_selo]),
        ft.ElevatedButton("ДОБАВИТЬ В БАЗУ", on_click=lambda _: None, bgcolor="#40C4FF", color="black", width=500), # Тут привяжи свою функцию если надо
        ft.Divider(),
        v_search,
        vlan_list_display
    ], visible=False, scroll=ft.ScrollMode.AUTO)

    ip_view = ft.Column([
        ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: navigate("main")), ft.Text("База IP")]),
        ft.Row([ip_vlan, ip_addr, ip_selo]),
        ft.ElevatedButton("ДОБАВИТЬ IP", on_click=lambda _: None, bgcolor="#40C4FF", color="black", width=500), # И тут
        ft.Divider(),
        ip_search,
        ip_list_display
    ], visible=False, scroll=ft.ScrollMode.AUTO)

    settings_view = ft.Column([
        ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: navigate("main")), ft.Text("Настройки")]),
        ft.Text("Версия движка: 2.1 (Твой рабочий + Dropdown fix)")
    ], visible=False)

    v_search.on_change = update_vlan_list
    ip_search.on_change = update_ip_list

    page.add(main_view, priem_view, spisanie_view, history_view, vlan_view, ip_view, settings_view)
    refresh_all()

ft.app(target=main)
