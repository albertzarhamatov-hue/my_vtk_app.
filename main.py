import flet as ft
import os
import tempfile
import socket
import webbrowser
import shutil
from datetime import datetime

# --- ИСПРАВЛЕННАЯ НАСТРОЙКА ПУТЕЙ ДЛЯ ANDROID ---
def get_path():
    # Используем временную директорию, которая всегда доступна приложению на Android
    if os.name != 'nt':
        base = os.path.join(tempfile.gettempdir(), "VTK_DATA_SAFE")
    else:
        # Для Windows на рабочем столе или в Temp
        base = os.path.join(os.path.expanduser("~"), "Desktop", "VTK_NEW_PRO_Data")
    
    if not os.path.exists(base): 
        os.makedirs(base, exist_ok=True)
    return base

BASE_DIR = get_path()
SKLAD_DIR = os.path.join(BASE_DIR, "sklad")
VLAN_DIR = os.path.join(BASE_DIR, "vlan")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
IP_BS_DIR = os.path.join(BASE_DIR, "ip_bs")
PHOTOS_DIR = os.path.join(BASE_DIR, "photos")

# Создаем все папки при запуске
for d in [SKLAD_DIR, VLAN_DIR, LOGS_DIR, IP_BS_DIR, PHOTOS_DIR]:
    os.makedirs(d, exist_ok=True)

def main(page: ft.Page):
    page.title = "VTK_NEW PRO"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = ft.padding.only(top=50, left=20, right=20, bottom=20)
    page.scroll = "adaptive"

    main_accent = "#30D5C8"
    txt_size_multi = 1.0
    temp_photo_path = ft.Text("")

    def on_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            temp_photo_path.value = e.files[0].path
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_result)
    page.overlay.append(file_picker)

    def open_details(title, text, photo_fn=None):
        content = ft.Column([ft.Text(text, selectable=True, size=16 * txt_size_multi)], tight=True, scroll="adaptive")
        p_path = None
        if photo_fn:
            photo_fn = photo_fn.replace(" ", "_")
            potential_path = os.path.join(PHOTOS_DIR, photo_fn + ".jpg")
            if os.path.exists(potential_path):
                p_path = potential_path
        
        if p_path:
            content.controls.insert(0, ft.Image(src=p_path, width=300, border_radius=10))
        
        dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=content,
            actions=[ft.TextButton("ЗАКРЫТЬ", on_click=lambda _: setattr(dlg, "open", False) or page.update())]
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def show_menu(e=None):
        page.clean()
        page.add(
            ft.Text("VTK_NEW PRO", size=30 * txt_size_multi, weight="bold", color=main_accent),
            ft.Divider(height=10, color="transparent"),
            ft.Row([
                ft.Container(content=ft.Text("ПРИЕМКА", weight="bold", size=14*txt_size_multi), bgcolor="#1C1C1E", padding=30, expand=True, border_radius=15, on_click=show_priemka),
                ft.Container(content=ft.Text("ИСТОРИЯ", weight="bold", size=14*txt_size_multi), bgcolor="#1C1C1E", padding=30, expand=True, border_radius=15, on_click=show_history),
            ], spacing=10),
            ft.Container(
                content=ft.Column([
                    ft.ListTile(title=ft.Text("Списание на абонента", size=16*txt_size_multi), on_click=show_spisanie),
                    ft.ListTile(title=ft.Text("База VLAN", size=16*txt_size_multi), on_click=show_vlan),
                    ft.ListTile(title=ft.Text("IP Адреса БС", size=16*txt_size_multi), on_click=show_ip_bs),
                    ft.ListTile(title=ft.Text("IP РОУТЕРА (ВЕБКА)", color="#FFD700", size=16*txt_size_multi), leading=ft.Icon(ft.Icons.WIFI, color="#FFD700"), on_click=show_router_scanner),
                ]), bgcolor="#1C1C1E", border_radius=15, padding=10
            ),
            ft.Divider(height=20, color="transparent"),
            ft.ElevatedButton("НАСТРОЙКИ", icon=ft.Icons.SETTINGS, on_click=show_settings, width=400)
        )

    def show_settings(e=None):
        page.clean()
        def toggle_theme(e):
            page.theme_mode = ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
            page.bgcolor = "#FFFFFF" if page.theme_mode == ft.ThemeMode.LIGHT else "#000000"
            page.update()
        def toggle_contrast(e):
            nonlocal main_accent
            main_accent = "#0066FF" if main_accent == "#30D5C8" else "#30D5C8"
            show_settings()
        def set_font(size):
            nonlocal txt_size_multi
            txt_size_multi = size
            show_settings()
        page.add(
            ft.Text("НАСТРОЙКИ", size=25 * txt_size_multi, weight="bold"),
            ft.Switch(label="Светлая тема", value=page.theme_mode == ft.ThemeMode.LIGHT, on_change=toggle_theme),
            ft.Switch(label="Высокий контраст (Синий)", value=main_accent == "#0066FF", on_change=toggle_contrast),
            ft.Text("Размер шрифта:"),
            ft.Row([
                ft.ElevatedButton("Обычный", on_click=lambda _: set_font(1.0)),
                ft.ElevatedButton("Крупный", on_click=lambda _: set_font(1.3)),
            ]),
            ft.Divider(height=20),
            ft.ElevatedButton("<- НАЗАД", on_click=show_menu)
        )

    def show_priemka(e=None):
        page.clean()
        f_name = ft.TextField(label="Товар", bgcolor="#1C1C1E")
        f_count = ft.TextField(label="Количество", value="1", bgcolor="#1C1C1E")
        f_sn = ft.TextField(label="S/N (через пробел)", bgcolor="#1C1C1E", multiline=True)
        sklad_view = ft.Column(scroll="adaptive", height=300)

        def refresh():
            sklad_view.controls.clear()
            if os.path.exists(SKLAD_DIR):
                for f in sorted(os.listdir(SKLAD_DIR)):
                    if f.endswith(".txt"):
                        with open(os.path.join(SKLAD_DIR, f), "r", encoding="utf-8") as file:
                            d = file.read().split("|")
                            info = f"Товар: {d[0]}\nSN: {d[1]}\nКол-во: {d[2]}\nДата: {d[3]}"
                            sklad_view.controls.append(ft.Row([ft.Container(content=ft.Text(f"📦 {d[0]} | SN: {d[1]} | ({d[2]} шт.)", size=12*txt_size_multi), expand=True, on_click=lambda _, fn=d[0], txt=info: open_details("Детали", txt, fn)), ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda _, fn=f: [os.remove(os.path.join(SKLAD_DIR, fn)), refresh()])]))
            page.update()

        def save(e):
            if f_name.value:
                sns = f_sn.value.strip().split()
                count = int(f_count.value) if f_count.value.isdigit() else 1
                item_name_clean = f_name.value.replace(' ','_')
                if temp_photo_path.value:
                    shutil.copy(temp_photo_path.value, os.path.join(PHOTOS_DIR, f"{item_name_clean}.jpg"))
                    temp_photo_path.value = ""
                if not sns:
                    fn = f"{item_name_clean}_BN_{datetime.now().strftime('%H%M%S%f')}.txt"
                    with open(os.path.join(SKLAD_DIR, fn), "w", encoding="utf-8") as f: f.write(f"{f_name.value}|Б/Н|{count}|{datetime.now().strftime('%d.%m.%y')}")
                else:
                    for sn in sns:
                        fn = f"{item_name_clean}_{sn}_{datetime.now().strftime('%H%M%S%f')}.txt"
                        with open(os.path.join(SKLAD_DIR, fn), "w", encoding="utf-8") as f: f.write(f"{f_name.value}|{sn}|1|{datetime.now().strftime('%d.%m.%y')}")
                refresh()

        page.add(ft.Text("ПРИЕМКА", size=20*txt_size_multi), f_name, f_count, f_sn, ft.Row([ft.ElevatedButton("ФОТО", on_click=lambda _: file_picker.pick_files()), ft.ElevatedButton("ДОБАВИТЬ", on_click=save, bgcolor=main_accent, color="black")]), sklad_view, ft.ElevatedButton("<- НАЗАД", on_click=show_menu))
        refresh()

    def show_spisanie(e=None):
        page.clean()
        def get_opts(): 
            options = []
            if os.path.exists(SKLAD_DIR):
                for f in os.listdir(SKLAD_DIR):
                    if f.endswith(".txt"):
                        with open(os.path.join(SKLAD_DIR, f), "r", encoding="utf-8") as file:
                            d = file.read().split("|")
                            options.append(ft.dropdown.Option(key=f, text=f"{d[0]} (SN: {d[1]})"))
            return options
        dd = ft.Dropdown(label="Товар", options=get_opts(), bgcolor="#1C1C1E")
        acc, addr = ft.TextField(label="Л/С", bgcolor="#1C1C1E"), ft.TextField(label="Адрес", bgcolor="#1C1C1E")
        cnt = ft.TextField(label="Количество", value="1", bgcolor="#1C1C1E")
        def do_work(e):
            if not dd.value or not acc.value: return
            src = os.path.join(SKLAD_DIR, dd.value)
            with open(src, "r", encoding="utf-8") as f: d = f.read().split("|")
            total = int(d[2]); rem = int(cnt.value) if cnt.value.isdigit() else 1
            if rem > total: rem = total
            with open(os.path.join(LOGS_DIR, "history.txt"), "a", encoding="utf-8") as log:
                log.write(f"{datetime.now().strftime('%d.%m %H:%M')} | {d[0]} | {rem}шт | {acc.value} | {addr.value}\n")
            if total - rem <= 0: os.remove(src)
            else:
                with open(src, "w", encoding="utf-8") as f: f.write(f"{d[0]}|{d[1]}|{total-rem}|{d[3]}")
            show_menu()
        page.add(ft.Text("СПИСАНИЕ", size=20*txt_size_multi), dd, cnt, acc, addr, ft.ElevatedButton("ЗАВЕРШИТЬ", on_click=do_work, bgcolor=main_accent, color="black"), ft.ElevatedButton("<- НАЗАД", on_click=show_menu))

    def show_history(e=None):
        page.clean()
        search_hist = ft.TextField(label="Поиск по истории", bgcolor="#1C1C1E", on_change=lambda e: refresh(e.control.value))
        lv = ft.Column(scroll="adaptive", height=500)
        h_path = os.path.join(LOGS_DIR, "history.txt")
        def refresh(query=""):
            lv.controls.clear()
            if os.path.exists(h_path):
                with open(h_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for line in reversed(lines):
                        if not query or query.lower() in line.lower():
                            parts = line.split("|")
                            item_name = parts[1].strip() if len(parts) > 1 else None
                            txt = line.strip()
                            lv.controls.append(ft.Container(content=ft.Text(txt, size=12*txt_size_multi, color=main_accent), padding=10, border_radius=10, bgcolor="#1C1C1E", on_click=lambda _, t=txt, n=item_name: open_details("Запись истории", t, n)))
            page.update()
        page.add(ft.Text("ИСТОРИЯ СКЛАДА", size=20*txt_size_multi, weight="bold"), search_hist, lv, ft.ElevatedButton("<- НАЗАД", on_click=show_menu, width=400))
        refresh()

    def show_vlan(e=None):
        page.clean()
        v_num = ft.TextField(label="VLAN", bgcolor="#1C1C1E", expand=1)
        v_ip = ft.TextField(label="IP", bgcolor="#1C1C1E", expand=2)
        v_city = ft.TextField(label="Село", bgcolor="#1C1C1E", expand=2)
        v_search = ft.TextField(label="ПОИСК VLAN / СЕЛО", bgcolor="#1C1C1E", on_change=lambda e: refresh(e.control.value))
        v_list = ft.Column(scroll="adaptive", height=400)

        def refresh(query=""):
            v_list.controls.clear()
            if os.path.exists(VLAN_DIR):
                for f in os.listdir(VLAN_DIR):
                    if f.endswith(".txt"):
                        with open(os.path.join(VLAN_DIR, f), "r", encoding="utf-8") as file:
                            content = file.read()
                            if not query or query.lower() in content.lower():
                                v_list.controls.append(ft.Row([ft.Container(content=ft.Text(f"🌐 {content}", size=13*txt_size_multi), expand=True), ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda _, fn=f: [os.remove(os.path.join(VLAN_DIR, fn)), refresh()])]))
            page.update()

        def add_vlan(e):
            if v_num.value and v_city.value:
                with open(os.path.join(VLAN_DIR, f"v_{datetime.now().strftime('%H%M%S%f')}.txt"), "w", encoding="utf-8") as f: f.write(f"VLAN: {v_num.value} | IP: {v_ip.value} | Село: {v_city.value}")
                refresh()

        page.add(ft.Text("БАЗА VLAN", size=20*txt_size_multi), ft.Row([v_num, v_ip, v_city]), ft.ElevatedButton("ДОБАВИТЬ", on_click=add_vlan, bgcolor=main_accent, color="black"), v_search, v_list, ft.ElevatedButton("<- НАЗАД", on_click=show_menu))
        refresh()

    def show_ip_bs(e=None):
        page.clean()
        s, i = ft.TextField(label="Объект", bgcolor="#1C1C1E"), ft.TextField(label="IP", bgcolor="#1C1C1E")
        bs_search = ft.TextField(label="ПОИСК ОБЪЕКТА", bgcolor="#1C1C1E", on_change=lambda e: refresh(e.control.value))
        bs_list = ft.Column(scroll="adaptive", height=400)
        
        def refresh(query=""):
            bs_list.controls.clear()
            if os.path.exists(IP_BS_DIR):
                for f in os.listdir(IP_BS_DIR):
                    if f.endswith(".txt"):
                        with open(os.path.join(IP_BS_DIR, f), "r", encoding="utf-8") as file:
                            content = file.read()
                            if not query or query.lower() in content.lower():
                                bs_list.controls.append(ft.Row([ft.Container(content=ft.Text(f"📍 {content}", size=14*txt_size_multi), expand=True), ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda _, fn=f: [os.remove(os.path.join(IP_BS_DIR, fn)), refresh()])]))
            page.update()
            
        page.add(ft.Text("IP БС", size=20*txt_size_multi), s, i, ft.ElevatedButton("ДОБАВИТЬ", on_click=lambda _: [open(os.path.join(IP_BS_DIR, f"b_{datetime.now().strftime('%H%M%S%f')}.txt"),"w", encoding="utf-8").write(f"{s.value} - {i.value}"), refresh()]), bs_search, bs_list, ft.ElevatedButton("НАЗАД", on_click=show_menu))
        refresh()

    def show_router_scanner(e=None):
        page.clean()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))
            rip = f"{sock.getsockname()[0].rsplit('.', 1)[0]}.1"
            sock.close()
        except: rip = "192.168.1.1"
        page.add(ft.Text("IP РОУТЕРА"), ft.Text(rip, size=40*txt_size_multi, color=main_accent), ft.ElevatedButton("ВЕБКА", on_click=lambda _: webbrowser.open(f"http://{rip}")), ft.ElevatedButton("НАЗАД", on_click=show_menu))

    show_menu()

ft.app(target=main)
