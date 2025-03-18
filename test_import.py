try:
    from google.auth.credentials import Credentials
    print("google.auth.credentials imported successfully!")
except ModuleNotFoundError as e:
    print("Module not found:", e)