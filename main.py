import os
import tempfile
from datetime import datetime

# Отключаем ctypes для предотвращения сбоя (Fatal Signal) on Android
os.environ["FLET_PYTHON_NO_CTYPES"] = "1"

import flet as ft

# --- ОБНОВЛЕННЫЙ ДВИЖОК: СТАБИЛЬНЫЕ ПУТИ ---
def get_path():
    # Для Android/iOS используем внутреннюю директорию приложения
    # Для Windows/Linux используем папку в профиле пользователя или temp
    if os.getenv("ANDROID_DATA") or os.getenv("EXTERNAL_STORAGE"):
        base = os.path.expanduser("~/Sklad_Set_Data")
    elif os.name != 'nt':
        base = os.path.join(os.getcwd(), "Sklad_Set_Data")
    else:
        base = os.path.join(os.getenv('APPDATA') or tempfile.gettempdir(), "Sklad_Set_Final_App")
    
    if not os.path.exists(base): 
        os.makedirs(base, exist_ok=True)
    return base

BASE_DIR = get_path()
STOCK_DIR = os.path.join(BASE_DIR, "stock")
VLAN_DIR = os.path.join(BASE_DIR, "vlan")
IP_DIR = os.path.join(BASE_DIR, "ip_base")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Гарантируем создание всех поддиректорий
for d in [STOCK_DIR, VLAN_DIR, IP_DIR, LOGS_DIR]:
    os.makedirs(d, exist_ok=True)

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.padding = 20
    page.title = "Склад и Сеть"

    # --- ФУНКЦИИ НАСТРОЕК ---
    def change_font_size(e):
        page.text_style = ft.TextStyle(size=int(e.control.value))
        page.update()

    def change_app_color(color_name):
        page.theme = ft.Theme(color_scheme_seed=color_name)
        page.update()
    
    current_photo_path = ft.Ref[str]()
    current_photo_path.current = None

    def show_detail_log(content):
        parts = content.split(" | IMG:")
        text_content = parts[0]
        image_path = parts[1] if len(parts) > 1 else None

        dlg_content = ft.Column(tight=True, spacing=10)
        dlg_content.controls.append(ft.Text(text_content))
        
        if image_path and os.path.exists(image_path):
            dlg_content.controls.append(ft.Image(src=image_path, width=300, height=300, fit=ft.ImageFit.CONTAIN, border_radius=10))

        dlg = ft.AlertDialog(
            title=ft.Text("Детали записи"),
            content=dlg_content,
            actions=[ft.TextButton("Закрыть", on_click=lambda e: page.close(dlg))],
        )
        page.open(dlg)

    def on_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            current_photo_path.current = e.files[0].path
            page.snack_bar = ft.SnackBar(ft.Text(f"Выбрано фото: {e.files[0].name}"))
            page.snack_bar.open = True
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_result)
    page.overlay.append(file_picker)

    # --- ЭЛЕМЕНТЫ ПРИЁМКИ ---
    product_in = ft.TextField(label="Название товара", border_color="#40C4FF")
    
    unit_type = ft.SegmentedButton(
        selected={"sn"},
        allow_empty_selection=False,
        on_change=lambda e: toggle_unit_fields(e),
        segments=[
            ft.Segment(value="sh", label=ft.Text("Штуки"), icon=ft.Icon(ft.Icons.LOOKS_ONE)),
            ft.Segment(value="m", label=ft.Text("Метры"), icon=ft.Icon(ft.Icons.STRAIGHTEN)),
            ft.Segment(value="sn", label=ft.Text("S/N"), icon=ft.Icon(ft.Icons.QR_CODE_2)),
        ],
    )

    count_in = ft.TextField(label="Количество / Метраж", border_color="#40C4FF", value="1")
    serial_in = ft.TextField(label="Серийные номера (через пробел)", visible=True)
    priem_results = ft.Column(spacing=10)

    def toggle_unit_fields(e):
        serial_in.visible = ("sn" in unit_type.selected)
        page.update()

    # --- ЭЛЕМЕНТЫ СПИСАНИЯ ---
    product_drop = ft.Dropdown(label="Выбрать товар", border_color="#40C4FF")
    serial_drop = ft.Dropdown(label="Выбрать SN / Метраж / Кол-во", border_color="#40C4FF")
    count_out = ft.TextField(label="Сколько списать", value="1")
    account_out = ft.TextField(label="Лицевой счет")
    address_out = ft.TextField(label="Адрес")
    history_list = ft.Column(spacing=10)

    v_vlan = ft.TextField(label="VLAN", width=100); v_ip = ft.TextField(label="IP адрес", width=150)
    v_selo = ft.TextField(label="Село", width=150); v_search = ft.TextField(label="Поиск по селу", prefix_icon=ft.Icons.SEARCH)
    vlan_list_display = ft.Column(spacing=10)

    ip_vlan = ft.TextField(label="VLAN", width=100); ip_addr = ft.TextField(label="IP адрес", width=150)
    ip_selo = ft.TextField(label="Село", width=150); ip_search = ft.TextField(label="Поиск по селу", prefix_icon=ft.Icons.SEARCH)
    ip_list_display = ft.Column(spacing=10)

    def update_serials(e):
        selected_prod = product_drop.value
        serial_drop.options = []
        if selected_prod and os.path.exists(STOCK_DIR):
            for f in os.listdir(STOCK_DIR):
                with open(os.path.join(STOCK_DIR, f), "r", encoding="utf-8") as file:
                    data = file.read().split("|")
                    if data[0] == selected_prod:
                        unit = " м." if data[2] == "m" else (" шт." if data[2] == "sh" else "")
                        display_val = f"{data[1]} ({data[3]}{unit})" if data[2] in ["m", "sh"] else data[1]
                        serial_drop.options.append(ft.dropdown.Option(key=f, text=display_val))
        serial_drop.value = None
        page.update()

    product_drop.on_change = update_serials

    def update_history_list():
        history_list.controls.clear()
        if os.path.exists(LOGS_DIR):
            files = sorted(os.listdir(LOGS_DIR), reverse=True)
            for f in files:
                if "log_priem" in f: continue
                with open(os.path.join(LOGS_DIR, f), "r", encoding="utf-8") as file:
                    content = file.read()
                    display_text = content.split(" | IMG:")[0]
                    history_list.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.HISTORY_OUTLINED, color="grey"),
                                ft.Text(display_text, size=12, expand=True, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                                ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color="red700", on_click=lambda _, p=f: delete_history_item(p))
                            ]),
                            bgcolor="#1E1E20", padding=10, border_radius=10,
                            on_click=lambda _, c=content: show_detail_log(c)
                        )
                    )
        page.update()

    def delete_history_item(filename):
        path = os.path.join(LOGS_DIR, filename)
        if os.path.exists(path): os.remove(path)
        update_history_list()

    def refresh_all():
        priem_results.controls.clear()
        unique_products = set()
        if os.path.exists(STOCK_DIR):
            for f in os.listdir(STOCK_DIR):
                try:
                    with open(os.path.join(STOCK_DIR, f), "r", encoding="utf-8") as file:
                        data = file.read().split("|")
                        if len(data) < 4: continue
                        unique_products.add(data[0])
                        unit = "м" if data[2] == "m" else ("ш" if data[2] == "sh" else "")
                        priem_results.controls.append(
                            ft.Container(
                                content=ft.Row([
                                    ft.Text(f"{data[0]} | {data[1]} | {data[3]} {unit}", size=14, expand=True),
                                    ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color="red400", on_click=lambda _, p=f: [os.remove(os.path.join(STOCK_DIR, p)), refresh_all()])
                                ]),
                                bgcolor="#1E1E20", padding=10, border_radius=8
                            )
                        )
                except: continue
        product_drop.options = [ft.dropdown.Option(p) for p in sorted(list(unique_products))]
        update_history_list(); page.update()

    def add_to_stock(e):
        name = product_in.value.strip()
        mode = list(unit_type.selected)[0]
        val_str = count_in.value.strip()
        if not name or not val_str: return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        if mode == "m":
            fname = f"m_{timestamp}.txt"
            with open(os.path.join(STOCK_DIR, fname), "w", encoding="utf-8") as f: f.write(f"{name}|Метраж|m|{val_str}")
        elif mode == "sh":
            fname = f"sh_{timestamp}.txt"
            with open(os.path.join(STOCK_DIR, fname), "w", encoding="utf-8") as f: f.write(f"{name}|Штучно|sh|{val_str}")
        else:
            qty = int(val_str) if val_str.isdigit() else 1
            sns = serial_in.value.strip().split()
            for i in range(qty):
                sn = sns[i] if i < len(sns) else "Б/Н"
                fname = f"sn_{timestamp}_{i}.txt"
                with open(os.path.join(STOCK_DIR, fname), "w", encoding="utf-8") as f: f.write(f"{name}|{sn}|sn|1")
        
        log_name = f"log_priem_{timestamp}.txt"
        log_text = f"ПРИЁМ: {name} ({val_str} {mode})"
        if current_photo_path.current: log_text += f" | IMG:{current_photo_path.current}"
        with open(os.path.join(LOGS_DIR, log_name), "w", encoding="utf-8") as f: f.write(log_text)
        
        product_in.value = ""; count_in.value = "1"; serial_in.value = ""
        current_photo_path.current = None; refresh_all()

    def complete_spisanie(e):
        if not product_drop.value or not serial_drop.value: return
        file_path = os.path.join(STOCK_DIR, serial_drop.value)
        if not os.path.exists(file_path): return
        
        with open(file_path, "r", encoding="utf-8") as f: data = f.read().split("|")
        prod_name, sn_val, mode, current_qty = data[0], data[1], data[2], float(data[3])
        minus_qty = float(count_out.value.replace(",", ".")) if count_out.value else 1.0
        unit = "м" if mode == "m" else ("ш" if mode == "sh" else "шт")
        
        if mode in ["m", "sh"]:
            new_qty = current_qty - minus_qty
            if new_qty <= 0: 
                os.remove(file_path)
                final_spisano = f"{current_qty} {unit} (полностью)"
            else:
                with open(file_path, "w", encoding="utf-8") as f: f.write(f"{prod_name}|{sn_val}|{mode}|{new_qty}")
                final_spisano = f"{minus_qty} {unit} (остаток {new_qty})"
        else: 
            os.remove(file_path)
            final_spisano = f"SN: {sn_val}"
            
        log_name = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.txt"
        log_text = f"{datetime.now().strftime('%d.%m %H:%M')} | {prod_name} | Списано: {final_spisano} | Л/С: {account_out.value} | Адрес: {address_out.value}"
        if current_photo_path.current: log_text += f" | IMG:{current_photo_path.current}"
        
        with open(os.path.join(LOGS_DIR, log_name), "w", encoding="utf-8") as f: f.write(log_text)
        account_out.value = ""; address_out.value = ""; count_out.value = "1"
        current_photo_path.current = None; refresh_all(); navigate("history")

    def navigate(view):
        main_view.visible = (view == "main"); priem_view.visible = (view == "priem")
        spisanie_view.visible = (view == "spisanie"); history_view.visible = (view == "history")
        vlan_view.visible = (view == "vlan"); ip_view.visible = (view == "ip")
        settings_view.visible = (view == "settings"); page.update()

    def menu_card(icon, text, view_name):
        return ft.Container(content=ft.ListTile(leading=ft.Icon(icon, color="#40C4FF"), title=ft.Text(text), on_click=lambda _: navigate(view_name)), bgcolor="#1E1E20", border_radius=12, margin=8)

    main_view = ft.Column([
        ft.Text("Склад и Сеть", size=24, weight="bold", color="#40C4FF"),
        menu_card(ft.Icons.DOWNLOAD, "Приём материала", "priem"),
        menu_card(ft.Icons.PERSON_REMOVE, "Списание на абонента", "spisanie"),
        menu_card(ft.Icons.HISTORY, "История списаний", "history"),
        menu_card(ft.Icons.STORAGE, "База VLAN", "vlan"),
        menu_card(ft.Icons.LANGUAGE, "IP адреса", "ip"),
        menu_card(ft.Icons.SETTINGS, "Настройки", "settings"),
    ])

    priem_view = ft.Column([
        ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: navigate("main")), ft.Text("Приём материала")]),
        product_in, ft.Text("Тип учета:", size=12, color="grey"), unit_type, count_in, serial_in,
        ft.Row([ft.ElevatedButton("ФОТО", icon=ft.Icons.IMAGE, on_click=lambda _: file_picker.pick_files()), ft.ElevatedButton("ДОБАВИТЬ", on_click=add_to_stock, bgcolor="#40C4FF", color="black", expand=True)]),
        ft.Divider(), priem_results
    ], visible=False, scroll=ft.ScrollMode.AUTO)

    spisanie_view = ft.Column([
        ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: navigate("main")), ft.Text("Списание")]),
        product_drop, serial_drop, count_out, account_out, address_out,
        ft.Row([ft.ElevatedButton("ФОТО СПИСАНИЯ", icon=ft.Icons.IMAGE, on_click=lambda _: file_picker.pick_files()), ft.ElevatedButton("ЗАВЕРШИТЬ", on_click=complete_spisanie, bgcolor="#FF5252", color="white", expand=True)])
    ], visible=False)

    history_view = ft.Column([
        ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: navigate("main")), ft.Text("История списаний")]),
        history_list
    ], visible=False, scroll=ft.ScrollMode.AUTO)

    vlan_view = ft.Column([
        ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: navigate("main")), ft.Text("База VLAN")]),
        ft.Row([v_vlan, v_ip, v_selo]), ft.ElevatedButton("ДОБАВИТЬ", on_click=lambda _: None, bgcolor="#40C4FF", color="black", width=500),
        ft.Divider(), v_search, vlan_list_display
    ], visible=False, scroll=ft.ScrollMode.AUTO)

    ip_view = ft.Column([
        ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: navigate("main")), ft.Text("База IP")]),
        ft.Row([ip_vlan, ip_addr, ip_selo]), ft.ElevatedButton("ДОБАВИТЬ", on_click=lambda _: None, bgcolor="#40C4FF", color="black", width=500),
        ft.Divider(), ip_search, ip_list_display
    ], visible=False, scroll=ft.ScrollMode.AUTO)

    settings_view = ft.Column([
        ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: navigate("main")), ft.Text("Настройки")]),
        ft.Container(
            padding=15,
            bgcolor="#1E1E20",
            border_radius=12,
            content=ft.Column([
                ft.Text("Шрифт приложения:", size=16),
                ft.Slider(min=10, max=24, value=14, divisions=7, label="{value}", on_change=change_font_size),
                ft.Divider(),
                ft.Text("Цвет оформления:", size=16),
                ft.Row([
                    ft.IconButton(ft.Icons.CIRCLE, icon_color="blue", on_click=lambda _: change_app_color("blue")),
                    ft.IconButton(ft.Icons.CIRCLE, icon_color="green", on_click=lambda _: change_app_color("green")),
                    ft.IconButton(ft.Icons.CIRCLE, icon_color="orange", on_click=lambda _: change_app_color("orange")),
                    ft.IconButton(ft.Icons.CIRCLE, icon_color="red", on_click=lambda _: change_app_color("red")),
                ])
            ])
        ),
        ft.Text("Версия движка: 2.4 ALBERT STABLE", color="grey", size=12)
    ], visible=False)

    page.add(main_view, priem_view, spisanie_view, history_view, vlan_view, ip_view, settings_view)
    refresh_all()

ft.app(target=main)
