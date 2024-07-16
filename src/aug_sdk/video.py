import os
import requests
import time

from typing import Callable

CHUNK_SIZE = 10 * 1024 * 1024  # 10 MB

class AugmendVideoClient:
    def __init__(self, api_key: str, root_host: str = "augmend.com", log_callback: Callable[[str], None] = None, verify_ssl: bool = True):
        self.api_key = api_key
        self.root_host = root_host
        self.log_callback = log_callback
        self.verify_ssl = verify_ssl
    
    def _log(self, msg: str):
        if self.log_callback:
            self.log_callback(msg)
    
    
    def upload_video(self, file_path: str) -> str:
        r"""Uploads a video and waits for it to finish processing.

        Parameters:
        file_path (str): Path of the file to upload
        """
        start_video_response = self._start_video_import_multipart()
        if not start_video_response:
            raise Exception('Failed to start video import')

        video_id = start_video_response['video_id']
        video_server = start_video_response['video_server']
        web_server = start_video_response['server']
        token = start_video_response['token']

        url = f'https://{video_server}/api/v0/video_import_multipart'
        headers = {
            'Authorization': f'Bearer {self.api_key}',
        }

        total_size = os.path.getsize(file_path)
        total_chunks = (total_size // CHUNK_SIZE) + (1 if total_size % CHUNK_SIZE else 0)

        with open(file_path, 'rb') as f:
            for chunk_index in range(total_chunks):
                chunk_offset = chunk_index * CHUNK_SIZE
                f.seek(chunk_offset)
                chunk_data = f.read(CHUNK_SIZE)

                files = {'file': (os.path.basename(file_path), chunk_data)}
                data = {
                    'video_id': video_id,
                    'token': token,
                    'dzchunkindex': str(chunk_index),
                    'dztotalchunkcount': str(total_chunks),
                    'dzchunkbyteoffset': str(chunk_offset),
                }

                response = requests.post(url, headers=headers, files=files, data=data, verify=self.verify_ssl)
                response.raise_for_status()
                self._log(f'Chunk {chunk_index + 1}/{total_chunks} uploaded successfully')

        wid = self._finish_video_import(web_server, video_id)
        if not wid:
            raise Exception('Failed to finish video import')
        
        self._wait_for_video_processing(wid)
        return wid

    def _start_video_import_multipart(self):
        url = f'https://{self.root_host}/api/v0/start_video_import_multipart'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
        }
        body = {
            'video_name': 'API video',
        }

        response = requests.post(url, headers=headers, json=body, verify=self.verify_ssl)
        response.raise_for_status()
        data = response.json()
        if 'error' in data:
            msg = f"Error from start_video_import_multipart API: {data['error']}"
            self._log(msg)
            raise Exception(msg)
        return data

    def _finish_video_import(self, web_server: str, video_id: str):
        url = f'https://{web_server}/api/v0/finish_video_import'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
        }
        body = {
            'video_id': video_id,
        }

        response = requests.post(url, headers=headers, json=body, verify=self.verify_ssl)
        response.raise_for_status()
        data = response.json()
        if 'error' in data:
            msg = f"Error from finish_video_import API: {data['error']}"
            self._log(msg)
            raise Exception(msg)
        
        wid = data['workspaceId']
        return wid

    def _wait_for_video_processing(self, wid: str):
        last_state = -1000
        while True:
            time.sleep(15)
            url = f'https://{self.root_host}/replay/{wid}/etl/0'
            headers = {
                'Authorization': f'Bearer {self.api_key}',
            }
            response = requests.get(url, headers=headers, verify=self.verify_ssl)
            data = response.json()
            state = data['state']
            desc = data['desc']
            if state != last_state:
                self._log(f"Current state is: {state} - {desc}")
                last_state = state
            if state == 0:
                return

    def get_document(self, wid: str, document_type: str):
        r"""Retrieves a document from a processed video.

        Parameters:
        wid (str): The id of the workspace (returned from upload_video).
        document_type (str): The type of document to retrieve. Valid values are "steps", "card", "chapters", "synopsis", "title", "keywords", "questions", "async"
        """
        url = f'https://{self.root_host}/replay/{wid}/document/{document_type}'
        headers = {
            'Authorization': f'Bearer {self.api_key}',
        }
        response = requests.get(url, headers=headers, verify=self.verify_ssl)
        data = response.json()
        document = data[document_type]
        return document