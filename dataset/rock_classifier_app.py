import flet as ft
import numpy as np
from PIL import Image
import io

# --- Rock Classes ---
ROCK_CLASSES = [
    "Basalt", "Chert", "Coal", "Gneiss", "Granite",
    "Limestone", "Marble", "Obsidian", "Pumice",
    "Sandstone", "Slate", "Travertine"
]

# Dummy model prediction (replace with your MindSpore inference later)
def predict_rock_class(image_bytes):
    import random
    return random.choice(ROCK_CLASSES)


def main(page: ft.Page):
    page.title = "Rock Classifier"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.window_width = 700
    page.window_height = 800
    page.padding = 30
    page.scroll = ft.ScrollMode.AUTO

    # --- Gradient Background (Radial: light grey -> grey) ---
    # Center is a light grey and it fades to a medium grey at the edges.
    # Customize `colors` (hex) and `stops` (0.0-1.0) to tweak the fade.
    page.bgcolor = None
    page.gradient = ft.RadialGradient(
        center=ft.alignment.top_center,
        radius=1.0,
        colors=["#f3f4f6", "#d1d5db", "#9ca3af"],
        stops=[0.0, 0.6, 1.0],
    )

    # --- Text Elements ---
    title = ft.Text(
        "Rock Classification System",
        size=32,
        weight=ft.FontWeight.BOLD,
        color=ft.colors.WHITE
    )
    subtitle = ft.Text(
        "Upload a rock image to identify its type",
        size=18,
        color=ft.colors.GREY_300
    )

    # --- Image Preview ---
    img_preview = ft.Image(
        src="",
        width=350,
        height=350,
        fit=ft.ImageFit.CONTAIN,
        border_radius=15,
    )

    # --- Prediction Output ---
    prediction_text = ft.Text(
        "",
        size=22,
        weight=ft.FontWeight.BOLD,
        color=ft.colors.BLUE_300
    )

    # --- File Picker ---
    file_picker = ft.FilePicker()
    selected_file_path = ft.Text("", visible=False)

    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            file = e.files[0]
            selected_file_path.value = file.path
            img_preview.src = file.path
            img_preview.update()
            prediction_text.value = ""
            prediction_text.update()
        else:
            prediction_text.value = "No image selected."
            prediction_text.color = ft.colors.RED
            prediction_text.update()

    file_picker.on_result = on_file_picked
    page.overlay.append(file_picker)

    # --- Buttons ---
    upload_button = ft.ElevatedButton(
        text="Upload Rock Image",
        icon=ft.icons.UPLOAD_FILE,
        bgcolor=ft.colors.BLUE_400,
        color=ft.colors.WHITE,
        on_click=lambda _: file_picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.IMAGE
        ),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            elevation=6,
        ),
    )

    def classify_click(e):
        if not selected_file_path.value:
            prediction_text.value = "Please upload an image first!"
            prediction_text.color = ft.colors.RED
            page.update()
            return

        with open(selected_file_path.value, "rb") as f:
            image_bytes = f.read()

        predicted_label = predict_rock_class(image_bytes)
        prediction_text.value = f"Predicted Rock Type: {predicted_label}"
        prediction_text.color = ft.colors.BLUE_300
        page.update()

    classify_button = ft.ElevatedButton(
        text="Classify Rock",
        icon=ft.icons.SEARCH,
        bgcolor=ft.colors.BLUE_500,
        color=ft.colors.WHITE,
        on_click=classify_click,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            elevation=6,
        ),
    )

    # --- Layout Directly on Background (no box) ---
    page.add(
        ft.Column(
            [
                title,
                subtitle,
                ft.Divider(height=25, color=ft.colors.TRANSPARENT),
                img_preview,
                ft.Divider(height=15, color=ft.colors.TRANSPARENT),
                upload_button,
                classify_button,
                ft.Divider(height=15, color=ft.colors.TRANSPARENT),
                prediction_text,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )


ft.app(target=main)
