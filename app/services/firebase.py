import firebase_admin
from firebase_admin import credentials, storage, firestore
import uuid
import io
import os
from PIL import Image
from google.cloud import storage as google_storage
from app.services.logger import setup_logger
from datetime import timedelta

logger = setup_logger(__name__)

class FirebaseManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not FirebaseManager._initialized:
            try:
                # Initialize Firebase if not already initialized
                if not firebase_admin._apps:
                    cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred, {
                        'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET')
                    })
                self.bucket = storage.bucket()
                logger.info(f"Firebase initialized with bucket: {self.bucket}")
                FirebaseManager._initialized = True
                logger.info("Firebase initialized successfully")
            except Exception as e:
                logger.error(f"Firebase initialization failed: {str(e)}")
                raise
    
    def upload_image(self, image_data, filename=None, expiration_minutes: int = 10080):  # 7 days = 7 * 24 * 60 = 10080
        """ Upload image to Firebase Storage and return a signed URL valid for specified duration. """
        try:
            if not filename:
                filename = f"images/{uuid.uuid4()}.png"
            
            if image_data is None:
                logger.error("No image data provided for upload")
                return None

            # Upload to Firebase
            blob = self.bucket.blob(filename)
            blob.upload_from_string(image_data._image_bytes, content_type="image/png")
            logger.info(f"Uploaded image to Firebase bucket: {filename}")

            # Generate signed URL
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=expiration_minutes),
                method="GET"
            )
            
            expiration_days = expiration_minutes / (24 * 60)
            logger.info(f"Generated signed URL (valid for {expiration_days:.1f} days): {signed_url}")
            
            return signed_url

        except AttributeError as e:
            logger.error(f"Invalid image data format: {str(e)}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Failed to upload image to Firebase: {str(e)}", exc_info=True)
            return None
