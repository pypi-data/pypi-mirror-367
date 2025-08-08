import requests
from bs4 import BeautifulSoup
import os, json
import time
import shutil
from urllib.parse import quote
import re
from datetime import datetime

def autosave(token=None, create_calendar=None, downloaded=None, delete_calendar=False, delete_draftfiles=False):
    system = {"token":token, "create_calendar":create_calendar, "downloaded":downloaded, "delete_calendar":delete_calendar, "delete_draftfiles":delete_draftfiles}
    open("autosave", "w").write(json.dumps(system))
def loadsave():
    if os.path.exists("autosave"):
        return json.loads(open("autosave", "r").read())
    else:
        return {"token":None, "create_calendar":None, "downloaded":None, "delete_calendar":False, "delete_draftfiles":False}
def clearsave():
    os.unlink("autosave")

def hora():
    hora_actual = datetime.now().strftime("%H:%M:%S")
    return hora_actual

def formato_tiempo(segundos):
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segundos_restantes = int(segundos % 60)
    return f"{horas:02d}:{minutos:02d}:{segundos_restantes:02d}"

def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.2f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.2f%s%s" % (num, 'Yi', suffix)

def genbar(porcentaje, ancho=20):
    porcentaje = max(0, min(100, porcentaje))
    completos = int(round(ancho * porcentaje / 100))
    vacios = ancho - completos
    barra = f"⟦{'▣' * completos}{'▢' * vacios}⟧"
    return barra

def get_src(html):
    return re.findall(r'src="([^"]+)"', html)

class BitFlush:
    def __init__(self):
        self.host = "https://aula.scu.sld.cu"
        self.username = "luisernestorb95"
        self.password = "Luisito1995*"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36"})
        self.sesskey = None
    def _login(self):
        _login_url = "https://aula.scu.sld.cu/login/index.php"
        while True:
            try:
                _gettoken = self.session.get(_login_url)
                break
            except:
                time.sleep(3)
                continue
        if "Actualmente ha iniciado sesión como" in _gettoken.text:
            return True
        logintoken = BeautifulSoup(_gettoken.text,"html.parser").find('input',{'name':'logintoken'})["value"]
        while True:
            try:
                _signin = self.session.post(_login_url, data={"logintoken":logintoken, "username":self.username, "password":self.password})
                break
            except:
                time.sleep(3)
                continue
        if "Área personal" in _signin.text:
            self.sesskey = _signin.text.split('"sesskey":"')[1].split('"')[0]
            return True
        else:
            return False
    def _new_draftfile(self):
        while True:
            try:
                _service = self.session.post(f"https://aula.scu.sld.cu/lib/ajax/service.php?sesskey={self.sesskey}&info=core_get_fragment", json=[{"index":0,"methodname":"core_get_fragment","args":{"component":"calendar","callback":"event_form","contextid":2,"args":[{"name":"courseid","value":1}]}}]).json()[0]["data"]["html"]
                break
            except:
                time.sleep(3)
                continue
        self.userid = BeautifulSoup(_service,"html.parser").find('input',{'name':"userid"})["value"]
        self.context = int(_service.split("ctx_id=")[1].split("&")[0])
        self.itemid = BeautifulSoup(_service,"html.parser").find('input',{'name':"description[itemid]"})["value"]
        while True:
            try:
                _managefile = self.session.get(f"https://aula.scu.sld.cu/lib/editor/atto/plugins/managefiles/manage.php?elementid=id_description&context={self.context}&areamaxbytes=-1&maxbytes=0&subdirs=0&return_types=15&removeorphaneddrafts=0&itemid={self.itemid}")
                break
            except:
                time.sleep(3)
                continue
        self.client_id = _managefile.text.split('"client_id":"')[1].split('"')[0]
    def _import_draftfile(self, token):
        token = token.split("-")
        self.client_id = token[0]
        self.itemid = token[1]
    def _create_calendar(self, token, urls):
        purls = []
        for u in urls:
            purls.append(f"%3Cp%20dir%3D%22ltr%22%20style%3D%22text-align%3A%20left%3B%22%3E%3Cimg%20src%3D%22{quote(u, safe='&=')}%22%20alt%3D%22%22%20width%3D%22100%22%20height%3D%22100%22%20role%3D%22presentation%22%20class%3D%22img-fluid%20atto_image_button_text-bottom%22%3E%3Cbr%3E%3C%2Fp%3E")
        while True:
            try:
                _create = self.session.post(f"https://aula.scu.sld.cu/lib/ajax/service.php?sesskey={self.sesskey}&info=core_calendar_submit_create_update_form", json=[{"index":0,"methodname":"core_calendar_submit_create_update_form","args":{"formdata":f"id=0&userid=711&modulename=&instance=0&visible=1&eventtype=user&sesskey={self.sesskey}&_qf__core_calendar_local_event_forms_create=1&mform_showmore_id_general=1&name={token}&timestart%5Bday%5D=10&timestart%5Bmonth%5D=7&timestart%5Byear%5D=2025&timestart%5Bhour%5D=23&timestart%5Bminute%5D=47&description%5Btext%5D={''.join(purls)}&description%5Bformat%5D=1&description%5Bitemid%5D=72498574&location=&duration=0"}}])
                break
            except:
                time.sleep(3)
                self._login()
                continue
        return _create.json()
    def _delete_calendar(self, eventid):
        while True:
            try:
                _delete = self.session.post(f"https://aula.scu.sld.cu/lib/ajax/service.php?sesskey={self.sesskey}&info=core_calendar_delete_calendar_events", json=[{"index":0,"methodname":"core_calendar_delete_calendar_events","args":{"events":[{"eventid":eventid,"repeat":False}]}}])
                break
            except:
                time.sleep(3)
                self._login()
                continue
        return _delete.json()
    def list(self):
        _listdata = self.session.post("https://aula.scu.sld.cu/repository/draftfiles_ajax.php?action=list", data={"sesskey":self.sesskey, "client_id":self.client_id, "filepath":"/", "itemid":self.itemid})
        return _listdata.json()
    def delete(self, filename):
        while True:
            try:
                _deldata = self.session.post("https://aula.scu.sld.cu/repository/draftfiles_ajax.php?action=delete", data={"sesskey":self.sesskey, "client_id":self.client_id, "filepath":"/", "itemid":self.itemid, "filename":filename})
                break
            except:
                time.sleep(3)
                self._login()
                continue
        return _deldata.json()

def download(filename, session, urls, callback=None):
    part_headers = []
    total_size = 0
    for url in urls:
        intents = 0
        while True:
            try:
                response = session.head(url, allow_redirects=True)
                response.raise_for_status()
                size = int(response.headers.get('content-length', 0))
                part_headers.append({'size': size, 'url': url})
                total_size += size
                break
            except requests.exceptions.RequestException as e:
                intents += 1
                if intents < 3:
                    continue
                else:
                    return 0, "DOWNLOAD_ERROR_404"

    downloaded_size = 0
    if os.path.exists(filename):
        downloaded_size = os.path.getsize(filename)

    if downloaded_size >= total_size and total_size > 0:
        if callback:
            callback(downloaded_size, total_size)
        return total_size, None
    
    with open(filename, 'ab') as f:
        cumulative_size = 0
        for part in part_headers:
            part_size = part['size']
            part_url = part['url']
            if downloaded_size >= cumulative_size + part_size:
                cumulative_size += part_size
                continue

            offset = 0

            if downloaded_size > cumulative_size:
                offset = downloaded_size - cumulative_size

            headers = {'Range': f'bytes={offset}-'}
            intents = 0
            while True:
                try:
                    response = session.get(part_url, headers=headers, stream=True, allow_redirects=True)
                    response.raise_for_status()
    
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            if callback:
                                callback(downloaded_size, total_size)
                    break
                except requests.exceptions.RequestException as e:
                    intents += 1
                    if intents < 3:
                        continue
                    else:
                        return 0, "C_ERROR"
            cumulative_size += part_size
    return total_size, None
            
def printF(text):
    try:
        width = shutil.get_terminal_size().columns
    except OSError:
        width = 80
    if len(text) >= width:
        text = text[:width - 1]
    print(text.ljust(width), end='\r')

url = "https://m-odepruebaparasubida.onrender.com"

downloads = 1
while True:
    autoS = loadsave()
    if not autoS["token"]:
        printF(" ⟪ ⚙ ⟫ BUSCANDO ARCHIVOS...")
        files = requests.get(url+"/telegram").json()
        if len(files) > 0:
            tim = time.time()
            filename = files[0]["name"]
            while True:
                try:
                    code = requests.post(url+"/download_telegram", json={"filename":filename}).json()["code"]
                    break
                except:
                    time.sleep(5)
                    continue
            while True:
                while True:
                    try:
                        progress = requests.post(url+"/progress", json={"code":code}).json()
                        break
                    except:
                        time.sleep(5)
                        continue
                percentage = round((progress['current']/progress['total'])*100,1)
                printF(f"  ▲ ⟪ ⚙ {percentage}% ⟫  ⦁  {progress['current']}/{progress['total']} {genbar(percentage)}")
                if progress['current']==progress['total']:
                    token = progress["token"]
                    autosave(token=token)
                    break
        else:
            time.sleep(2)
            continue
    else:
        token = autoS["token"]
        tim = time.time()
    if not token:
        continue
    flush = BitFlush()
    flush._login()
    printF(" ⟪ ⚙ ⟫ IMPORTANDO BORRADOR...")
    flush._import_draftfile(token)
    flush_list = flush.list()["list"]
    filename = flush_list[0]["filename"].replace(".000", "")
    urls = []
    for f in flush_list:
        urls.append(f["url"])
    if not autoS["create_calendar"]:
        printF(" ⟪ ⚙ ⟫ CREANDO CALENDARIO...")
        calendar = flush._create_calendar(token,urls)
        autosave(token=token, create_calendar=calendar)
    else:
        calendar = autoS["create_calendar"]
        tim = time.time()
    if not calendar:
        continue
    furls = get_src(calendar[0]["data"]["event"]["description"])
    def callback(current, total):
        percentage = round((current/total)*100,1)
        printF(f"  ▼ ⟪ ⚙ {percentage}% ⟫  ⦁  {sizeof_fmt(current)}/{sizeof_fmt(total)} {genbar(percentage)}")
    if not autoS["downloaded"]:
        total_size, error = download(filename, flush.session, furls, callback=callback)
        autosave(token=token, create_calendar=calendar, downloaded={"total_size":total_size, "error":error})
    else:
        total_size = autoS["downloaded"]["total_size"]
        error = autoS["downloaded"]["error"]
    if not autoS["delete_calendar"]:
        printF(" ⟪ ⚙ ⟫ ELIMINANDO CALENDARIO...")
        flush._delete_calendar(calendar[0]["data"]["event"]["id"])
        autosave(token=token, create_calendar=calendar, downloaded={"total_size":total_size, "error":error}, delete_calendar=True)
    if not autoS["delete_draftfiles"]:
        printF(" ⟪ ⚙ ⟫ LIMPIANDO BORRADOR...")
        for f in flush_list:
            flush.delete(f["filename"])
        autosave(token=token, create_calendar=calendar, downloaded={"total_size":total_size, "error":error}, delete_calendar=True, delete_draftfiles=True)
    tem = time.time()
    if error:
        printF(f" ⟪ {str(downloads).zfill(3)} ⟫ ⟪ {hora()} ⟫ ⟪ {error} ⟫ ⟪ TIEMPO | {formato_tiempo(tem-tim)} ⟫ ⟪ {str(downloads).zfill(3)} ⟫ ⟪ {filename} ⟫ ")
    else:
        printF(f" ⟪ {str(downloads).zfill(3)} ⟫ ⟪ TOTAL | {sizeof_fmt(total_size)} ⟫ ⟪ TIEMPO | {formato_tiempo(tem-tim)} ⟫ ⟪ {filename} ⟫ ")
    downloads += 1
    clearsave()
    print()
    time.sleep(2)
