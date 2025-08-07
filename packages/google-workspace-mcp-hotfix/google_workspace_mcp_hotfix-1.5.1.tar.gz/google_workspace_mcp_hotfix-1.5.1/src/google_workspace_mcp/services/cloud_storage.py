"""
Google Cloud Storage service for temporary image storage with signed URLs.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any

from google.cloud import storage
from google_workspace_mcp.auth import gauth
from google_workspace_mcp.services.base import BaseGoogleService

logger = logging.getLogger(__name__)


class CloudStorageService(BaseGoogleService):
    """Service for Google Cloud Storage operations with signed URLs."""

    def __init__(self):
        """Initialize the Cloud Storage service."""
        # Don't call super().__init__ since we're using different auth
        self.project_id = "slack-bot-arclio-1749249337"  # Your project
        self.bucket_name = "arclio-temp-slides-images"
        
        # Use the same credentials as other Google services
        credentials = gauth.get_credentials()
        self.client = storage.Client(credentials=credentials, project=self.project_id)
        
        # Ensure bucket exists
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Create the bucket if it doesn't exist."""
        try:
            bucket = self.client.bucket(self.bucket_name)
            if not bucket.exists():
                logger.info(f"Creating Cloud Storage bucket: {self.bucket_name}")
                bucket = self.client.create_bucket(self.bucket_name, location="us-central1")
                logger.info(f"Created bucket: {self.bucket_name}")
            else:
                logger.info(f"Using existing bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Error with bucket setup: {e}")
            # Continue anyway - bucket might exist but we lack permissions to check

    def copy_drive_image_to_storage(self, drive_file_id: str, drive_service=None) -> dict[str, Any]:
        """
        Copy a private Google Drive image to Cloud Storage.

        Args:
            drive_file_id: The Google Drive file ID
            drive_service: Optional Drive service instance

        Returns:
            Dict with storage info or error details
        """
        try:
            # Import Drive service if not provided
            if not drive_service:
                from .drive import DriveService
                drive_service = DriveService()

            # Get the file from Drive
            logger.info(f"Retrieving Drive file: {drive_file_id}")
            drive_file = drive_service.service.files().get(fileId=drive_file_id).execute()
            file_name = drive_file.get("name", f"image_{drive_file_id}")
            
            # Get the file content as bytes
            file_content = drive_service.service.files().get_media(fileId=drive_file_id).execute()
            
            # Create a unique filename for storage
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            storage_filename = f"temp_images/{timestamp}_{drive_file_id}_{file_name}"
            
            # Upload to Cloud Storage
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(storage_filename)
            
            logger.info(f"Uploading to Cloud Storage: {storage_filename}")
            blob.upload_from_string(file_content, content_type=drive_file.get("mimeType", "image/jpeg"))
            
            logger.info(f"Successfully uploaded to Cloud Storage: gs://{self.bucket_name}/{storage_filename}")
            
            return {
                "success": True,
                "storage_path": f"gs://{self.bucket_name}/{storage_filename}",
                "blob_name": storage_filename,
                "original_filename": file_name,
                "drive_file_id": drive_file_id,
            }

        except Exception as e:
            error_msg = f"Failed to copy Drive image to storage: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def generate_signed_url(self, blob_name: str, expiration_minutes: int = 15) -> dict[str, Any]:
        """
        Generate a signed URL for temporary public access.

        Args:
            blob_name: The name of the blob in storage
            expiration_minutes: Minutes until URL expires (default 15)

        Returns:
            Dict with signed URL or error details
        """
        try:
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(blob_name)
            
            # Generate signed URL with expiration
            expiration_time = datetime.now() + timedelta(minutes=expiration_minutes)
            
            logger.info(f"Generating signed URL for {blob_name}, expires in {expiration_minutes} minutes")
            signed_url = blob.generate_signed_url(expiration=expiration_time, method="GET")
            
            return {
                "success": True,
                "signed_url": signed_url,
                "expires_at": expiration_time.isoformat(),
                "blob_name": blob_name,
            }

        except Exception as e:
            error_msg = f"Failed to generate signed URL: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def copy_and_get_signed_url(self, drive_file_id: str, expiration_minutes: int = 15) -> dict[str, Any]:
        """
        One-step operation: copy Drive image to storage and get signed URL.

        Args:
            drive_file_id: The Google Drive file ID
            expiration_minutes: Minutes until URL expires

        Returns:
            Dict with signed URL ready for Slides API
        """
        try:
            # Step 1: Copy to storage
            copy_result = self.copy_drive_image_to_storage(drive_file_id)
            if not copy_result.get("success"):
                return copy_result

            # Step 2: Generate signed URL
            blob_name = copy_result["blob_name"]
            url_result = self.generate_signed_url(blob_name, expiration_minutes)
            if not url_result.get("success"):
                return url_result

            # Return combined result
            return {
                "success": True,
                "signed_url": url_result["signed_url"],
                "expires_at": url_result["expires_at"],
                "storage_path": copy_result["storage_path"],
                "original_filename": copy_result["original_filename"],
                "drive_file_id": drive_file_id,
                "message": f"Private Drive image available via signed URL (expires in {expiration_minutes} min)",
            }

        except Exception as e:
            error_msg = f"Failed to copy and generate signed URL: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def cleanup_expired_files(self, max_age_hours: int = 1):
        """
        Clean up temporary files older than max_age_hours.

        Args:
            max_age_hours: Maximum age in hours before cleanup
        """
        try:
            bucket = self.client.bucket(self.bucket_name)
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            logger.info(f"Cleaning up files older than {max_age_hours} hours")
            
            deleted_count = 0
            for blob in bucket.list_blobs(prefix="temp_images/"):
                if blob.time_created.replace(tzinfo=None) < cutoff_time:
                    blob.delete()
                    deleted_count += 1
                    logger.debug(f"Deleted expired file: {blob.name}")
            
            logger.info(f"Cleaned up {deleted_count} expired temporary files")
            return {"success": True, "deleted_count": deleted_count}

        except Exception as e:
            error_msg = f"Failed to cleanup expired files: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
