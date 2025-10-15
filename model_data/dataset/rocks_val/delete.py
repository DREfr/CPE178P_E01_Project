import os
import shutil

# ✅ Folders you want to keep
keep_folders = [
    "Basalt", "Chert", "Coal", "Gneiss", "Granite", "Limestone",
    "Marble", "Obsidian", "Pumice", "Sandstone", "Slate", "Travertine"
]

# ✅ Current directory (where this .py file is located)
base_dir = os.getcwd()

for folder in os.listdir(base_dir):
    folder_path = os.path.join(base_dir, folder)
    if os.path.isdir(folder_path):
        if folder not in keep_folders:
            print(f"🗑️ Deleting folder: {folder_path}")
            shutil.rmtree(folder_path)
        else:
            print(f"✅ Keeping folder: {folder_path}")

print("\n✅ Cleanup complete — only selected rock folders remain.")
