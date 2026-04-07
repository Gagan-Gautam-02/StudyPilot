import json
from google.cloud import firestore
from app.config import config
import os

db = None

def get_db():
    global db
    if db is None:
        try:
            # First try default authentication or via GOOGLE_APPLICATION_CREDENTIALS
            if config.GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(config.GOOGLE_APPLICATION_CREDENTIALS):
                db = firestore.Client(project=config.PROJECT_ID, database="studypilot")
                print("Firestore client initialized with credentials.")
            else:
                # If no credentials, we might create a mock client or run in a default mode
                # Usually in Cloud Run, it auto-authenticates.
                db = firestore.Client(project=config.PROJECT_ID if config.PROJECT_ID else "mock-project-id", database="studypilot")
                print("Firestore client initialized with default environment.")
        except Exception as e:
            print(f"Failed to initialize Firestore: {e}")
            db = None # Application handle db as None gracefully
    return db
