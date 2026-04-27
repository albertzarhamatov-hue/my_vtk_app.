import os
# Отключаем ctypes для предотвращения сбоя (Fatal Signal) на Android
os.environ["FLET_PYTHON_NO_CTYPES"] = "1"

import flet as ft

def main(page: ft.Page):
    # Оставляем настройки как были
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.padding = 20

    # --- ХРАНИЛИЩЕ ДАННЫХ (БЕЗ ИЗМЕНЕНИЙ) ---
    stock = {}  
    vlan_base = [] 
    ip_base = []   

    # --- КОМПОНЕНТЫ ПРИЁМА (БЕЗ ИЗМЕНЕНИЙ) ---
    product_in = ft.TextField(label="Товар", border_color="#40C4FF")
    count_in = ft.TextField(label="Кол-во (напр. 10 или 1000м)", border_color="#40C4FF")
    serial_in = ft.TextField(label="Серийные номера (через пробел)")
    priem_results = ft.Column(spacing=10)

    # --- КОМПОНЕНТЫ VLAN (БЕЗ ИЗМЕНЕНИЙ) ---
    v_vlan = ft.TextField(label="VLAN", width=100)
    v_ip = ft.TextField(label="IP адрес", width=150)
    v_selo = ft.TextField(label="Село", width=150)
    v_search = ft.TextField(label="Поиск по селу", prefix_icon=ft.Icons.SEARCH, on_change=lambda e: update_vlan_list())
    vlan_list_display = ft.Column(spacing=10)

    # --- КОМПОНЕНТЫ IP АДРЕСОВ (БЕЗ ИЗМЕНЕНИЙ) ---
    ip_vlan = ft.TextField(label="VLAN", width=100)
    ip_addr = ft.TextField(label="IP адрес", width=150)
    ip_selo = ft.TextField(label="Село", width=150)
    ip_search = ft.TextField(label="Поиск по селу", prefix_icon=ft.Icons.SEARCH, on_change=lambda e: update_ip_list())
    ip_list_display = ft.Column(spacing=10)

    # --- ФУНКЦИИ (БЕЗ ИЗМЕНЕНИЙ СИМВОЛОВ) ---
    def on_product_change(e):
        name = product_drop.value
        if name in stock:
            options = []
            for item in stock[name]:
                if item[0] == "sn":
                    options.append(ft.dropdown.Option(item[1]))
                else:
                    options.append(ft.dropdown.Option(f"Метраж: {item[1]}м"))
            serial_drop.options = options
            serial_drop.value = options[0].key if options else None
        page.update()

    product_drop = ft.Dropdown(label="Выбрать товар", border_color="#40C4FF", on_change=on_product_change)
    serial_drop = ft.Dropdown(label="Выбрать SN или Метраж", border_color="#40C4FF")
    count_out = ft.TextField(label="Сколько списать (для метров)", value="1")
    account_out = ft.TextField(label="Лицевой счет")
    address_out = ft.TextField(label="Адрес")

    history_list = ft.Column(spacing=10)

    def show_details(details):
        dlg = ft.AlertDialog(title=ft.Text("Детали"), content=ft.Text(details),
                             actions=[ft.TextButton("ОК", on_click=lambda e: page.close(dlg))])
        page.overlay.append(dlg); dlg.open = True; page.update()

    def add_vlan(e):
        if v_vlan.value and v_selo.value:
            vlan_base.append({"vlan": v_vlan.value, "ip": v_ip.value, "selo": v_selo.value})
            v_vlan.value = ""; v_ip.value = ""; v_selo.value = ""
            update_vlan_list()

    def delete_vlan(item):
        vlan_base.remove(item)
        update_vlan_list()

    def update_vlan_list():
        vlan_list_display.controls.clear()
        search = v_search.value.lower()
        for item in vlan_base:
            if search in item["selo"].lower():
                vlan_list_display.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(f"Село: {item['selo']}", weight="bold"),
                                ft.Text(f"VLAN: {item['vlan']} | IP: {item['ip']}", color="grey")
                            ], expand=True),
                            ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda _, i=item: delete_vlan(i))
                        ]),
                        bgcolor="#1E1E20", padding=10, border_radius=10
                    )
                )
        page.update()

    def add_ip(e):
        if ip_addr.value and ip_selo.value:
            ip_base.append({"vlan": ip_vlan.value, "ip": ip_addr.value, "selo": ip_selo.value})
            ip_vlan.value = ""; ip_addr.value = ""; ip_selo.value = ""
            update_ip_list()

    def delete_ip(item):
        ip_base.remove(item)
        update_ip_list()

    def update_ip_list():
        ip_list_display.controls.clear()
        search = ip_search.value.lower()
        for item in ip_base:
            if search in item["selo"].lower():
                ip_list_display.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(f"Село: {item['selo']}", weight="bold"),
                                ft.Text(f"IP: {item['ip']} | VLAN: {item['vlan']}", color="grey")
                            ], expand=True),
                            ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda _, i=item: delete_ip(i))
                        ]),
                        bgcolor="#1E1E20", padding=10, border_radius=10
                    )
                )
        page.update()

    def update_all_lists():
        priem_results.controls.clear()
        for name, items in stock.items():
            display_info = []
            total_items = 0
            for itype, ival in items:
                if itype == "sn":
                    display_info.append(ival)
                    total_items += 1
                else:
                    display_info.append(f"{ival}м")
                    total_items += 1
            if total_items > 0:
                priem_results.controls.append(
                    ft.Container(content=ft.Column([ft.Text(name, weight="bold", size=16),
                    ft.Text(f"На складе: {', '.join(display_info)}", color="grey")]),
                    bgcolor="#1E1E20", padding=12, border_radius=10))
        product_drop.options = [ft.dropdown.Option(p) for p in stock.keys() if len(stock[p]) > 0]
        page.update()

    def add_to_stock(e):
        name = product_in.value.strip()
        raw_count = count_in.value.strip().lower()
        sns_list = serial_in.value.strip().split()
        if name and raw_count:
            if name not in stock: stock[name] = []
            if "м" in raw_count or "m" in raw_count:
                val = float(raw_count.replace("м","").replace("m",""))
                stock[name].append(["m", val])
            else:
                qty = int(raw_count)
                for i in range(qty):
                    sn = sns_list[i] if i < len(sns_list) else "Б/Н"
                    stock[name].append(["sn", sn])
            product_in.value = ""; count_in.value = ""; serial_in.value = ""
            update_all_lists()

    def complete_spisanie(e):
        name = product_drop.value
        selected_val = serial_drop.value
        try:
            minus_val = float(count_out.value)
        except: minus_val = 1.0
        if name and selected_val:
            target_item = None
            for i, item in enumerate(stock[name]):
                if item[0] == "sn" and item[1] == selected_val:
                    target_item = stock[name].pop(i)
                    info_sn = target_item[1]
                    break
                elif item[0] == "m" and f"Метраж: {item[1]}м" == selected_val:
                    if item[1] >= minus_val:
                        item[1] -= minus_val
                        info_sn = f"{minus_val}м (Остаток {item[1]}м)"
                        if item[1] <= 0: stock[name].pop(i)
                        target_item = True
                        break
            if target_item:
                full_info = f"Товар: {name}\nСписано: {info_sn}\nАдрес: {address_out.value}\nЛ/С: {account_out.value}"
                hist_item = ft.Container(content=ft.Row([ft.Column([ft.Text(f"Списано: {name}", weight="bold"),
                ft.Text(f"{info_sn} | {address_out.value}", size=12, color="grey")], expand=True),
                ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda _: history_list.controls.remove(hist_item) or page.update())]),
                bgcolor="#1E1E20", padding=10, border_radius=10, on_click=lambda _: show_details(full_info))
                history_list.controls.insert(0, hist_item)
                update_all_lists()
                navigate("history")

    # --- НОВЫЕ ФУНКЦИИ НАСТРОЕК ---
    def change_theme(e):
        page.bgcolor = "#000000" if e.control.value else "#121212"
        page.update()

    def change_font(e):
        new_size = int(e.control.value)
        # Принудительное обновление стилей для мобильных
        page.theme = ft.Theme(text_theme=ft.TextTheme(body_medium=ft.TextStyle(size=new_size)))
        page.update()

    def navigate(view):
        main_view.visible = (view == "main"); priem_view.visible = (view == "priem")
        spisanie_view.visible = (view == "spisanie"); history_view.visible = (view == "history")
        vlan_view.visible = (view == "vlan"); ip_view.visible = (view == "ip")
        settings_view.visible = (view == "settings")
        page.update()

    def menu_card(icon, text, view_name):
        return ft.Container(content=ft.ListTile(leading=ft.Icon(icon, color="#40C4FF"), title=ft.Text(text),
        on_click=lambda _: navigate(view_name)), bgcolor="#1E1E20", border_radius=12, margin=8)

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
        ft.Switch(label="Глубокий черный фон", on_change=change_theme),
        ft.Dropdown(
            label="Размер шрифта",
            on_change=change_font,
            options=[
                ft.dropdown.Option("14", "Маленький"),
                ft.dropdown.Option("18", "Средний"),
                ft.dropdown.Option("22", "Большой"),
            ],
            value="18"
        ),
    ], visible=False)

    page.add(main_view, priem_view, spisanie_view, history_view, vlan_view, ip_view, settings_view)

ft.app(target=main)
