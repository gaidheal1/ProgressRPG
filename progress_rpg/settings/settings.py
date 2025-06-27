import os

print("settings.py")
# Dynamically load the correct settings file based on the DJANGO_SETTINGS_MODULE environment variable
settings_module = os.getenv("DJANGO_SETTINGS_MODULE", "progress_rpg.settings.dev")
print(f"Loading settings module: {settings_module}")
exec(f"from {settings_module} import *")
