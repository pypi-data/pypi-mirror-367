import os
import json
import base64
from typing import Optional
from firebase_admin import firestore, storage, credentials, initialize_app
from firebase_admin.credentials import Certificate
from google.cloud.storage.bucket import Bucket
from google.cloud.storage.blob import Blob


class FireStore:
    """
    FireStore client for uploading files to Firebase Storage.

    Automatically initializes Firebase using:
    - Provided firebase_admin.credentials.Certificate
    - OR from base64-encoded env var FIREBASE_PRODUCTION_CREDENTIALS_BASE64
    """

    def __init__(self, storage_bucket: str, cert: Optional[Certificate] = None):
        """
        Initialize FireStore client.

        :param storage_bucket: Firebase Storage bucket name (e.g., 'my-bucket.appspot.com')
        :param cert: Optional firebase_admin.credentials.Certificate instance
        """
        self._initialize_firebase(storage_bucket=storage_bucket, cert=cert)

    def _initialize_firebase(self, storage_bucket: str, cert: Optional[Certificate]):
        if cert is None:
            # Load from base64-encoded environment variable
            encoded = os.getenv("FIREBASE_PRODUCTION_CREDENTIALS_BASE64")
            if not encoded:
                raise EnvironmentError("❌ FIREBASE_PRODUCTION_CREDENTIALS_BASE64 not set.")
            decoded = json.loads(base64.b64decode(encoded).decode("utf-8"))
            cert = credentials.Certificate(decoded)

        # Only initialize Firebase once
        if not firestore._apps:
            initialize_app(cert, {
                'storageBucket': storage_bucket
            })

        self.db: firestore.Client = firestore.client()
        self.bucket: Bucket = storage.bucket()

    def upload_to_storage(self, file_object, cloud_file_path):
        """
        Uploads a file object to Firebase Storage.

        :param file_object: File object to be uploaded.
        :param cloud_file_path: Path in Firebase Storage where the file should be uploaded.
        """
        blob: Blob = self.bucket.blob(cloud_file_path)
        blob.upload_from_filename(file_object)