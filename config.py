import os

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

CHUNK_SIZE = 8 * 1024 * 1024

LARGE_FILE_THRESHOLD = 16 * 1024 * 1024

MAX_WORKERS = 5