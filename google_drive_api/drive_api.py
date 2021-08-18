import argparse
import json
import os.path
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = [
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/drive',
]

FILE_ID = '0B2FJFuPO4g4wREVOeFl0X2ZLLXM'
SRC_PATH = None
DIST_PATH = None


def credentials_as_dict(credentials) -> dict:
    credentials_as_dict = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "id_token": credentials.id_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    return credentials_as_dict


def credentials_from_dict(credentials_dict: dict) -> Credentials:
    creds = Credentials(
        credentials_dict["token"],
        refresh_token=credentials_dict["refresh_token"],
        token_uri=credentials_dict["token_uri"],
        client_id=credentials_dict["client_id"],
        client_secret=credentials_dict["client_secret"],
        scopes=credentials_dict["scopes"]
    )

    return creds


def get_credentials() -> Credentials:
    creds = None
    token_filename = "token.json"

    if os.path.exists(token_filename):
        with open(token_filename, "r") as f:
            credentials_as_dict = json.load(f)
            creds = credentials_from_dict(credentials_as_dict)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_filename, "w") as f:
            f.write(creds.to_json())

    return creds


def get_list_files(service: None, page_size: int = 30, param=None):
    if not param:
        results = (
            service.files()
                .list(pageSize=page_size, fields="nextPageToken, files(id, name, mimeType)")
                .execute()
        )
    else:
        results = (
            service.files()
                .list(q=param, pageSize=page_size, fields="nextPageToken, files(id, name, mimeType)")
                .execute()
        )
    # print(type(results))

    items = results.get("files", [])
    # print(items)
    # if not items:
    #     print("Not found files")
    # else:
    #     print("Files:")
    #     for item in items:
    #         print(f'{item["name"]}  {item["id"]}   {item["mimeType"]}')

    return items


def get_file(service, src_path, dist_path):
    dist_path = os.path.normpath(dist_path)
    if '/' in src_path:
        folder_list = get_list_files(service=service, param="mimeType = 'application/vnd.google-apps.folder'")
        folder_id = None
        for folder in folder_list:
            # print(f"{folder['name']} {src_path.split('/')[0]}")
            if folder['name'] == src_path.split('/')[0]:
                folder_id = folder['id']
                break

        if folder_id:
            file_list = get_list_files(service=service, param=f"'{folder_id}' in parents")
            file_id = None
            for file in file_list:
                if file['name'] == src_path.split('/')[-1]:
                    file_id = file['id']
        else:
            raise ValueError("This folder doesn't exist")
    else:
        file_id = get_list_files(service=service, param=f"name = '{src_path.split('/')[-1]}'")

    if file_id:
        request = service.files().get_media(fileId=file_id)
        filename = os.path.join(dist_path, src_path.split('/')[-1])
        fh = io.FileIO(filename, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
    else:
        raise ValueError("This file doesn't exist")

    print(f"The file was successfully uploaded to computer!")


def put_file(service, src_path, dist_path):
    src_path = os.path.normpath(src_path)

    if '/' in dist_path:
        folder_name, file_name = dist_path.split('/')[0], dist_path.split('/')[-1]
        list_items = get_list_files(service)

        for item in list_items:
            if item['name'] == folder_name and item['mimeType'] == 'application/vnd.google-apps.folder':
                folder_id = item['id']
                break
        else:
            folder_id = create_folder(service, folder_name)

        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
    else:
        file_metadata = {
            'name': dist_path,
        }

    media = MediaFileUpload(src_path, resumable=True)
    r = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    print(f"The file was successfully uploaded to google drive!\nIt's id is '{r['id']}'")


def create_folder(service, folder_name):
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    file = service.files().create(body=file_metadata, fields='id').execute()
    return file.get('id')


def main():
    DOWNLOAD_PARAMETERS = ['method', 'src_path', 'dist_path']
    consol_parser = argparse.ArgumentParser(description='File download')
    for parameter in DOWNLOAD_PARAMETERS:
        consol_parser.add_argument(parameter, type=str)

    args = consol_parser.parse_args()
    method_download = args.method
    DIST_PATH = args.dist_path
    SRC_PATH = args.src_path
    credentials = get_credentials()
    drive_service = build("drive", "v3", credentials=credentials)
    if method_download == 'get':
        get_file(service=drive_service, src_path=SRC_PATH, dist_path=DIST_PATH)
    elif method_download == 'put':
        put_file(service=drive_service, src_path=SRC_PATH, dist_path=DIST_PATH)
    else:
        print("This script isn't able to do this")

    # DIST_PATH = 'C:/Users/Пользователь/Downloads/прив'
    # SRC_PATH = 'downloads/drive_api.py'
    # SRC_PATH = input()
    # DIST_PATH = input()


if __name__ == "__main__":
    main()
