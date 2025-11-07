import flet as ft
import websockets
import asyncio
import base64
import json
import csv
import os
import requests

# --- Rock Classes ---
ROCK_CLASSES = [
    "Basalt", "Chert", "Coal", "Gneiss", "Granite",
    "Limestone", "Marble", "Obsidian", "Pumice",
    "Sandstone", "Slate", "Travertine"
]

# --- Rock Info ---
ROCK_INFO = {
    "Basalt": "Dark volcanic rock formed from quickly cooled lava.",
    "Chert": "Hard, fine-grained sedimentary rock rich in silica.",
    "Coal": "Black fossil fuel made from ancient plant matter.",
    "Gneiss": "Metamorphic rock with distinct light and dark bands.",
    "Granite": "Coarse igneous rock made of quartz and feldspar.",
    "Limestone": "Sedimentary rock mainly of calcium carbonate.",
    "Marble": "Metamorphic rock from limestone, smooth and decorative.",
    "Obsidian": "Natural volcanic glass formed by rapid cooling.",
    "Pumice": "Light, porous volcanic rock that can float on water.",
    "Sandstone": "Sedimentary rock made of compacted sand grains.",
    "Slate": "Fine-grained rock that splits into flat sheets.",
    "Travertine": "Limestone formed by mineral springs, used in tiles."
}

DB_PATH = "database/db.csv"

# --- Utility Functions ---
def ensure_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["username", "password", "isadmin"])
            writer.writerow(["admin", "admin123", "1"])  # default admin

def load_users():
    ensure_db()
    users = []
    with open(DB_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            users.append(row)
    return users

def add_user(username, password, isadmin="0"):
    users = load_users()
    for user in users:
        if user["username"] == username:
            return False  # already exists
    with open(DB_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([username, password, isadmin])
    return True

def check_login(username, password):
    users = load_users()
    for user in users:
        if user["username"] == username and user["password"] == password:
            return user["isadmin"] == "1"
    return None

# --- Rock Prediction ---
async def send_prediction_request(image_path):
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
        image_data = base64.b64encode(image_bytes).decode("utf-8")

    async with websockets.connect("ws://localhost:8000/ws") as websocket:
        await websocket.send(json.dumps({
            "type": "predict",
            "data": image_data
        }))
        response = await websocket.recv()
        return json.loads(response)

# --- Main App ---
def main(page: ft.Page):
    page.title = "Rock Classification System"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.window_width = 700
    page.window_height = 700
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    ensure_db()  # make sure db file exists

    # ----------------- Admin Page -----------------
    def show_admin_page(username):
        page.clean()
        users = load_users()
        user_list = "\n".join([f"{u['username']}  |  Admin: {u['isadmin']}" for u in users])

        message = ft.Text("", color=ft.Colors.GREEN)
        file_picker = ft.FilePicker()
        page.overlay.append(file_picker)

        def on_file_picked(e: ft.FilePickerResultEvent):
            if e.files:
                ckpt_path = e.files[0].path
                try:
                    res = requests.post("http://localhost:8000/change_model", data={"ckpt_path": ckpt_path})
                    r = res.json()
                    message.value = r["message"]
                    message.color = ft.Colors.GREEN if r["status"] == "success" else ft.Colors.RED
                except Exception as ex:
                    message.value = f"Error: {ex}"
                    message.color = ft.Colors.RED
                page.update()

        file_picker.on_result = on_file_picked

        change_model_btn = ft.ElevatedButton(
            text="Change Model",
            icon=ft.Icons.SWAP_HORIZ,
            bgcolor=ft.Colors.AMBER_600,
            color=ft.Colors.WHITE,
            on_click=lambda _: file_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["ckpt"])

        )

        logout_btn = ft.ElevatedButton(text="Logout", on_click=lambda _: show_login_page())

        page.add(
            ft.Column(
                [
                    ft.Text(f"Welcome Admin {username}", size=22, weight=ft.FontWeight.BOLD),
                    ft.Text("Registered Users:", size=16, weight=ft.FontWeight.NORMAL),
                    ft.Text(user_list, size=14),
                    ft.Divider(),
                    change_model_btn,
                    message,
                    logout_btn
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

    # ----------------- Classify Page -----------------
    def show_classify_page(username):
        page.clean()
        title = ft.Text(f"Welcome, {username}!", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
        subtitle = ft.Text("Upload a rock image to identify its type", size=15, color=ft.Colors.GREY_300)
        img_preview = ft.Image(visible=False, width=250, height=250, fit=ft.ImageFit.CONTAIN, border_radius=10)
        prediction_text = ft.Text("", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_300)
        rock_info_text = ft.Text("", size=14, color=ft.Colors.GREY_800, text_align=ft.TextAlign.CENTER, width=450, italic=True)
        file_picker = ft.FilePicker()
        selected_file_path = ft.Text("", visible=False)

        def on_file_picked(e: ft.FilePickerResultEvent):
            if e.files:
                file = e.files[0]
                selected_file_path.value = file.path
                img_preview.src = file.path
                img_preview.visible = True
                prediction_text.value = ""
                rock_info_text.value = ""
                page.update()
            else:
                prediction_text.value = "No image selected."
                prediction_text.color = ft.Colors.RED
                page.update()

        file_picker.on_result = on_file_picked
        page.overlay.append(file_picker)

        def classify_click(e):
            if not selected_file_path.value:
                prediction_text.value = "Please upload an image first!"
                prediction_text.color = ft.Colors.RED
                page.update()
                return

            async def classify_async():
                try:
                    response = await send_prediction_request(selected_file_path.value)
                    if response.get("type") == "prediction":
                        predicted_class = response.get("class", "Unknown")
                        prediction_text.value = f"Predicted Rock Type: {predicted_class}"
                        prediction_text.color = ft.Colors.BLUE_300
                        rock_info_text.value = ROCK_INFO.get(predicted_class, "No description available.")
                    else:
                        prediction_text.value = "Error: Invalid response"
                        rock_info_text.value = ""
                except Exception as ex:
                    prediction_text.value = f"Connection error: {ex}"
                    prediction_text.color = ft.Colors.RED
                    rock_info_text.value = ""
                page.update()

            asyncio.run(classify_async())

        upload_button = ft.ElevatedButton(
            text="Upload", icon=ft.Icons.UPLOAD_FILE, bgcolor=ft.Colors.BLUE_400,
            color=ft.Colors.WHITE, on_click=lambda _: file_picker.pick_files(
                allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE
            ), width=130, height=40
        )

        classify_button = ft.ElevatedButton(
            text="Classify", icon=ft.Icons.SEARCH, bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE, on_click=classify_click, width=130, height=40
        )

        logout_button = ft.TextButton(text="Logout", on_click=lambda _: show_login_page())

        page.add(
            ft.Column(
                [
                    logout_button,
                    title,
                    subtitle,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    img_preview,
                    ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                    ft.Row([upload_button, classify_button], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
                    ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                    prediction_text,
                    rock_info_text,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

    # ----------------- Register Page -----------------
    def show_register_page():
        page.clean()
        reg_user = ft.TextField(label="Create Username", width=250)
        reg_pass = ft.TextField(label="Create Password", width=250, password=True, can_reveal_password=True)
        message = ft.Text("", color=ft.Colors.RED)

        def on_register(e):
            if not reg_user.value or not reg_pass.value:
                message.value = "All fields are required!"
            elif add_user(reg_user.value, reg_pass.value):
                message.value = "Registration successful! Please login."
                message.color = ft.Colors.GREEN
            else:
                message.value = "Username already exists!"
                message.color = ft.Colors.RED
            page.update()

        def back_to_login(e):
            show_login_page()

        register_btn = ft.ElevatedButton(text="Register", on_click=on_register)
        back_btn = ft.TextButton(text="Back to Login", on_click=back_to_login)

        page.add(
            ft.Column(
                [
                    ft.Text("Register New Account", size=24, weight=ft.FontWeight.BOLD),
                    reg_user,
                    reg_pass,
                    ft.Row([register_btn, back_btn], alignment=ft.MainAxisAlignment.CENTER),
                    message,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

    # ----------------- Login Page -----------------
    def show_login_page():
        page.clean()
        username = ft.TextField(label="Username", width=250)
        password = ft.TextField(label="Password", width=250, password=True, can_reveal_password=True)
        message = ft.Text("", color=ft.Colors.RED)

        def on_login(e):
            is_admin = check_login(username.value, password.value)
            if is_admin is None:
                message.value = "Invalid credentials!"
                page.update()
            elif is_admin:
                show_admin_page(username.value)
            else:
                show_classify_page(username.value)

        def on_register(e):
            show_register_page()

        login_btn = ft.ElevatedButton(text="Login", on_click=on_login, width=120)
        register_btn = ft.TextButton(text="Register", on_click=on_register)

        page.add(
            ft.Column(
                [
                    ft.Text("Welcome to the Rock Classification App!", size=24, weight=ft.FontWeight.BOLD),
                    username,
                    password,
                    ft.Row([login_btn, register_btn], alignment=ft.MainAxisAlignment.CENTER),
                    message,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

    # Start at login page
    show_login_page()

ft.app(target=main)
