import flet as ft
import websockets
import asyncio
import base64
import json

# --- Rock Classes ---
ROCK_CLASSES = [
    "Basalt", "Chert", "Coal", "Gneiss", "Granite",
    "Limestone", "Marble", "Obsidian", "Pumice",
    "Sandstone", "Slate", "Travertine"
]

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


def main(page: ft.Page):
    page.title = "Rock Classification System"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.window_width = 700
    page.window_height = 750
    page.padding = 30
    page.scroll = ft.ScrollMode.AUTO

    # --- Gradient Background ---
    page.gradient = ft.RadialGradient(
        center=ft.alignment.top_center,
        radius=1.0,
        colors=["#f3f4f6", "#d1d5db", "#9ca3af"],
        stops=[0.0, 0.6, 1.0],
    )

    # --- Text ---
    title = ft.Text("Rock Classification System", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    subtitle = ft.Text("Upload a rock image to identify its type", size=17, color=ft.Colors.GREY_300)

    # --- Image preview (auto-resizing) ---
    img_preview = ft.Image(
        visible=False,                     # hide until image is loaded
        width=320,
        height=320,
        fit=ft.ImageFit.CONTAIN,
        border_radius=15,
    )

    prediction_text = ft.Text("", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_300)

    # --- File Picker ---
    file_picker = ft.FilePicker()
    selected_file_path = ft.Text("", visible=False)

    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            file = e.files[0]
            selected_file_path.value = file.path
            img_preview.src = file.path
            img_preview.visible = True     # show image only after upload
            img_preview.update()
            prediction_text.value = ""
            prediction_text.update()
        else:
            prediction_text.value = "No image selected."
            prediction_text.color = ft.Colors.RED
            prediction_text.update()

    file_picker.on_result = on_file_picked
    page.overlay.append(file_picker)

    # --- Button actions ---
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
                else:
                    prediction_text.value = "Error: Invalid response"
                    prediction_text.color = ft.Colors.RED
            except Exception as ex:
                prediction_text.value = f"Connection error: {ex}"
                prediction_text.color = ft.Colors.RED
            page.update()

        asyncio.run(classify_async())

    # --- Buttons Side-by-Side ---
    upload_button = ft.ElevatedButton(
        text="Upload",
        icon=ft.Icons.UPLOAD_FILE,
        bgcolor=ft.Colors.BLUE_400,
        color=ft.Colors.WHITE,
        on_click=lambda _: file_picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.IMAGE,
        ),
        width=150,
        height=45,
    )

    classify_button = ft.ElevatedButton(
        text="Classify",
        icon=ft.Icons.SEARCH,
        bgcolor=ft.Colors.BLUE_600,
        color=ft.Colors.WHITE,
        on_click=classify_click,
        width=150,
        height=45,
    )

    buttons_row = ft.Row(
        [upload_button, classify_button],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
    )

    # --- Layout ---
    page.add(
        ft.Column(
            [
                title,
                subtitle,
                ft.Divider(height=25, color=ft.Colors.TRANSPARENT),
                img_preview,
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                buttons_row,
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                prediction_text,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

ft.app(target=main)
