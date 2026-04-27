import flet as ft
import traceback
import os

def main(page: ft.Page):
    page.title = "VTK_PRO"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    # Автоматически выбираем путь для лога (Android или Windows)
    if os.name == 'nt':
        log_path = "error_log.txt"
    else:
        log_path = "/storage/emulated/0/Download/error_log.txt"
    
    try:
        page.add(
            ft.Row(
                [ft.Text("VTK_PRO работает!", size=30, weight="bold", color="blue")],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Row(
                [ft.Text("Запуск прошел успешно", size=15)],
                alignment=ft.MainAxisAlignment.CENTER
            )
        )
        page.update()
        
    except Exception:
        with open(log_path, "w") as f:
            f.write(traceback.format_exc())

# Тот самый запуск, которого не хватало
if __name__ == "__main__":
    ft.app(target=main)