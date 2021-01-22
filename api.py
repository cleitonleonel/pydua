import os
import sys
import re
import requests
from datetime import datetime, date
from pychromepdf import ChromePDF
from bs4 import BeautifulSoup

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'
requests.packages.urllib3.disable_warnings()

URL_BASE = 'https://e-dua.sefaz.es.gov.br'
file_name = 'dua'

BASE_DIR = os.getcwd()

if sys.platform.startswith('win32'):
    system = 'Windows'
    PATH_TO_CHROME_EXE = r'C:\Progra~1\Google\Chrome\Application\chrome.exe'
    DRIVER_PATH = 'bin/chromedriver.exe'
elif sys.platform.startswith('linux'):
    system = 'Linux'
    PATH_TO_CHROME_EXE = '/usr/bin/google-chrome-stable'
    DRIVER_PATH = 'bin/chromedriver'


class Browser(object):

    def __init__(self):
        self.response = None
        self.current_page = None
        self.session = requests.Session()

    def headers(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        }
        return headers

    def send_request(self, method, url, **kwargs):
        response = self.session.request(method, url, **kwargs)
        if response.status_code == 200:
            return response

        return None


class DuaAPI(Browser):

    def __init__(self):
        super().__init__()
        self.current_dua_number = None
        self.headers = self.headers()

    def emit(self, amount, due_date, cpf_cnpj, description=''):
        document_type = "CPF"
        if len(cpf_cnpj) == 14:
            document_type = "CNPJ"

        data = {
            "txt_desc_orgao": "Fundo Rotativo do Sistema Penitenci&aacute;rio",  # "Secretaria de Estado da Justi&ccedil;a"
            "TXT_ORGAO": 60,
            "txt_desc_area": "Receitas Correntes",  # "Recebimento de Conv&ecirc;nios"
            "TXT_AREA": 13,  # 418
            "txt_desc_servico": "Comercializa&ccedil;&atilde;o de Produ&ccedil;&atilde;o Industrial - FRSP",  # "Pagamento do Fundo de Rotativo do Sistema Penitenci&aacute;rio - FRSP"
            "TXT_SERVICO": 22571,  # 22576
            "txt_hdcdrec": 1198,
            "txt_cdmunicip": 56251,
            "txt_seqmunic": 0o17,
            "TXT_NRDOCDEB": 000000000000,
            "txt_DTEMISSAO": date.today().strftime("%d/%m/%Y"),
            "txt_HREMISSAO": datetime.now().strftime('%H:%M:%S'),
            "TXT_REFERENCIA": "",
            "TXT_INFO_COMPLEMENTARES": description,
            "TXT_VENCIMENTO": due_date,
            "TXT_VLTRIB": amount,
            "TXT_VLMULTA": 000000000000,
            "TXT_VLJUROS": 000000000000,
            "TXT_VLCOR": 000000000000,
            "TXT_VLCRD": 000000000000,
            "TXT_VLTOTAL": "R$ ",
            "txt_sigla": document_type,
            "txt_cpfcnpj": cpf_cnpj,
            "txt_dsrazaosc": "++++++++++++++++++++++++++++++++++++++++++++++",
            "txt_TPTIPDUA": 1,
            "txt_APLICACAO": "TX",
            "txt_NRCONTROLE": "",
            "txt_NRCODDIGITAVEL": "",
            "txt_NRCODBARRA": "",
            "txt_REIMPRESSAO": "",
            "txt_TPORIGEMDB": "",
            "txt_PAGAMENTO": "",
            "msgRefis": "",
            "txt_tipdua": "",
            "txt_conversor": "",
            "txt_tipo": 1,
            "image.x": 44,
            "image.y": 8
        }

        self.response = self.send_request('GET', URL_BASE + '/aplicacoes/dua.asp', params=data, headers=self.headers, verify=False)

        if self.response:
            return self.response

        return False

    def get_dua_number(self):
        self.current_dua_number = re.compile(r'.*?N&ordm; (.*?)</b>').findall(self.response.text)[0]
        return self.current_dua_number

    def consult(self, cpf_cnpj, nr_dua):
        payload = {
            "hd_funcao": "reimprimir",
            "TXT_CPFCNPJ": cpf_cnpj,
            "TXT_NRDUA": nr_dua,
            "Submit": "Ok"
        }
        self.response = self.send_request('POST', URL_BASE + '/aplicacoes/consulta2.asp', data=payload, headers=self.headers, verify=False)

        if self.response:
            return self.get_data(self.response)

        return False

    def get_data(self, response):
        html = BeautifulSoup(response.text, "html.parser")
        items = html.find_all("b")
        stop = len(items)
        data_list = []
        for index in range(1, stop, 2):
            key = " ".join(items[index - 1].text.rsplit())
            value = " ".join(items[index].text.rsplit())
            print(key + ' ' + value)

        for index, item in enumerate(items):
            data_list.append(" ".join(items[index].text.replace(":", "").rsplit()))

        res_dct = {data_list[i]: data_list[i + 1] for i in range(0, len(data_list) - 1, 2)}
        return res_dct

    def get_pdf(self, template=None, nr_dua=None, native=False):
        cpdf = ChromePDF(PATH_TO_CHROME_EXE, DRIVER_PATH, sandbox=False)

        if not template:
            template = self.response.text
        else:
            with open(template, 'r', encoding='utf-8') as template_file:
                template = template_file.read()

        if not nr_dua:
            soup_template = BeautifulSoup(str(template).replace('alert', '//alert'), "html5lib")
        else:
            self.current_dua_number = nr_dua
            soup_template = template

        with open(f'{self.current_dua_number}-dua.html', 'w', encoding='utf-8') as html_file:
            html_file.write(str(soup_template).replace('<html><head>', '<html>\n<head>\n  <base href="https://e-dua.sefaz.es.gov.br">'))

        with open(f'{self.current_dua_number}-dua.html', 'r', encoding='utf-8') as html_file_string:
            html_byte_string = html_file_string.read()

        pdf_path = f'{BASE_DIR}/{self.current_dua_number}-{file_name}.pdf'
        with open(pdf_path, 'wb') as output_file:
            if system == 'Windows':
                cpdf.page_to_pdf(f'{BASE_DIR}/{html_file.name}', output_file, native=native)
            else:
                cpdf.html_string_to_pdf(html_byte_string, output_file, native=native)

        return pdf_path


if __name__ == '__main__':
    dua = DuaAPI()
    dua.emit(amount="2,00", due_date="20/03/2021", cpf_cnpj="12345678909", description='2 Blocos de concreto')
    print('GUARDE ESSE NÚMERO PARA CONSULTA POSTERIOR: ', dua.get_dua_number())
    dua.get_pdf()
    dua.consult(cpf_cnpj=12345678909, nr_dua=dua.get_dua_number())
    # dua.get_pdf(template='3349968726-dua.html', nr_dua='3349968726', native=False)
    # dua.consult(cpf_cnpj=12345678909, nr_dua=3349043900)
    # dua.consult(cpf_cnpj=12345678909, nr_dua=3348393517)
    # dua.consult(cpf_cnpj=12345678909, nr_dua=3348768340)
    # dua.consult(cpf_cnpj=12345678909, nr_dua=3348804916)
    # json_data = dua.consult(cpf_cnpj=12345678909, nr_dua=3348822906)
    # print(json_data)
