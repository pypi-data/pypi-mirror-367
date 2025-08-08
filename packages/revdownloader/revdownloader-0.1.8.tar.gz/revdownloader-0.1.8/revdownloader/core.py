import requests
from bs4 import BeautifulSoup
import os
import random
import time
import urllib3
import base64
from .config import Config
from typing import List

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class RevDownloader:
    def __init__(self):
        self.config = Config()
        self.totaldown = 0
        self.timed = 0
        self.named = "INDEFINIDO"
        
        # Crear directorio de descargas si no existe
        if not os.path.exists(self.config.DOWNLOAD_DIR):
            os.makedirs(self.config.DOWNLOAD_DIR)

    @staticmethod
    def sizeof_fmt(num, suffix='B'):
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.2f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.2f%s%s" % (num, 'Yi', suffix)

    @staticmethod
    def clear_console():
        os.system('cls' if os.name == 'nt' else 'clear')

    def download(self, url: str, name: str, session: requests.Session, total_size: int) -> None:
        downloaded = 0
        try:
            with session.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36"
            }, stream=True) as response:
                response.raise_for_status()
                with open(name, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            downloaded += 8192
                            self.totaldown += 8192
                            porcentaje = (self.totaldown/int(total_size))*100
                            s = round(time.time() - self.timed)
                            spaces = 17
                            rest = 100/spaces
                            barra = "  \033[32m|\033[0m\033[0m\033[1m\033[30m"+"\033[42m•"*round(porcentaje/rest)+"\033[40m•"*round((100-porcentaje)/rest)+f"\033[0m\033[1m {round(porcentaje,1)}% | {self.sizeof_fmt(self.totaldown)}     "
                            print(barra, end="\r")
                            file.write(chunk)
        except Exception as e:
            print("\n  \033[31m\033[1m|\033[0m\033[41m\033[30m\033[1m + ERROR - CONEXIÓN PERDIDA + \033[0m")
            raise e

    def download_files(self, urls: List[str]) -> None:
        self.clear_console()
        print("  \033[1m\033[33m|\033[30m\033[43m + PREPARANDO + \033[0m")
        
        for url in urls:
            parts = url.split("/")
            self.named = parts[-1]
            bitzero = parts[-2]
            k = parts[-4]
            
            size = k.split("-")[0]
            ide = k.split("-")[1]
            surl = parts[-3]
            
            if "-" in surl:
                urls = surl.split("-")
            else:
                urls = [surl]
            
            download_urls = []
            for url_part in urls:
                download_urls.append(
                    f"{self.config.HOST}/$$$call$$$/api/file/file-api/download-file?submissionFileId={url_part}&submissionId={self.config.REPO}&stageId=1"
                )
            
            index = 0
            ide = random.randint(1000, 9999)
            files = []
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36"
            }
            
            session = requests.Session()
            getToken = session.get(self.config.HOST + "/login", headers=headers, verify=False)
            token = BeautifulSoup(getToken.text, "html.parser").find('input', {'name': 'csrfToken'})
            login_data = {
                "password": self.config.PASSWORD,
                "remember": 1,
                "source": "",
                "username": self.config.USERNAME,
                "csrfToken": token['value'] if token else ""
            }
            login_response = session.post(
                f"{self.config.HOST}/login/signIn",
                data=login_data,
                headers=headers,
                verify=False
            )
            
            self.timed = time.time()
            self.clear_console()
            
            if len(self.named) > 10:
                namede = self.named[:7] + "..."
            else:
                namede = self.named
                
            print(f"  \033[32m|\033[0m\033[1m\033[42m\033[30m + DESCARGANDO + \033[0m {namede} | {self.sizeof_fmt(int(size))}")
            
            for url in download_urls:
                if url:
                    temp_filename = f"index_{ide}_{index}"
                    self.download(url, temp_filename, session, size)
                    files.append(temp_filename)
                    index += 1
            
            print("\n")
            with open(os.path.join(self.config.DOWNLOAD_DIR, self.named), "wb") as file:
                for f in files:
                    if bitzero == '1':
                        file.write(
                            open(f, "rb").read().replace(
                                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf6\x178U\x00\x00\x00\x00IEND\xaeB`\x82",
                                b''
                            )
                        )
                    elif bitzero == '2':
                        file.write(
                            base64.b64decode(
                                open(f, "r").read().replace('<!DOCTYPE html>\n<html lang="es">\n<bytes>', '').replace('</bytes></html>', '')
                            )
                        )
                    os.unlink(f)
            
            self.clear_console()
            print(f"\033[32mGUARDADO:\033[0m {os.path.join(self.config.DOWNLOAD_DIR, self.named)}")
            self.totaldown = 0
