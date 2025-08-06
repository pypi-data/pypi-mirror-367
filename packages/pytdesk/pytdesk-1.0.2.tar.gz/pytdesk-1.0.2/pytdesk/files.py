"""
Title: TalentDesk Files Module

Description:
    Provides access to file-related endpoints in the TalentDesk API.
    This module allows you to upload new files to the platform
    across various resources such as projects, tasks, opportunities, and invoices.

    Supported functionality includes:
        - Uploading new files via filename-based endpoints

Author: Scott Murray

Version: 1.0.0
"""

import os
import mimetypes
import base64


########################################################################################################################
########################################################################################################################
class FilesAPI:
    def __init__(self, client):
        self.client = client

########################################################################################################################
    def upload_file(self, file_path: str, remote_name: str = None) -> dict:
        """
        Upload a file to TalentDesk in base64-encoded format using _request().
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_name = remote_name or os.path.basename(file_path)

        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_name)
        if not mime_type:
            raise ValueError(f"Could not detect mime type for {file_name}")

        # Read and encode the file
        with open(file_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode("utf-8")

        # Create data URI payload
        data_uri = f"data:{mime_type};name={file_name};base64,{b64_data}"
        print(data_uri)

        # Construct correct headers
        headers = {
            "Content-Type": mime_type,
            "Accept": "application/json"
        }
        print(headers)

        # Ensure URL filename matches declared name
        return self.client._request(
            method="POST",
            endpoint=f"/files/{file_name}",  # must match remote_name exactly
            data=data_uri,
            headers=headers
        )
########################################################################################################################
########################################################################################################################
