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

    def emit(self, amount, due_date, cpf_cnpj, city_name, revenue_desc, description=''):
        revenue_params = {}
        if revenue_desc != '':
            revenue_params = dua.set_revenue(parameter=revenue_desc)
        params = {}
        if city_name != '':
            params = dua.city_params(parameter=city_name)
        document_type = "CPF"
        if len(cpf_cnpj) == 14:
            document_type = "CNPJ"

        data = {
            "txt_desc_orgao": "Fundo Rotativo do Sistema Penitenci&aacute;rio",
            "TXT_ORGAO": 60,
            "txt_desc_area": "Receitas Correntes",
            "TXT_AREA": 13,
            "txt_desc_servico": revenue_params['txt_desc_servico'],
            "TXT_SERVICO": revenue_params['TXT_SERVICO'],
            "txt_hdcdrec": revenue_params['txt_hdcdrec'],
            "txt_cdmunicip": params['code'],
            "txt_seqmunic": params['seq'],
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

    def city_params(self, parameter):
        data_list = [
            {'code': '56014',
             'seq': '001',
             'city': 'AFONSO CLAUDIO'
             },
            {'code': '57177',
             'seq': '002',
             'city': 'AGUA DOCE DO NORTE'
             },
            {'code': '57339',
             'seq': '003',
             'city': 'AGUIA BRANCA'
             },
            {'code': '56030',
             'seq': '004',
             'city': 'ALEGRE'
             },
            {'code': '56057',
             'seq': '005',
             'city': 'ALFREDO CHAVES'
             },
            {'code': '57193',
             'seq': '006',
             'city': 'ALTO RIO NOVO'
             },
            {'code': '56073',
             'seq': '007',
             'city': 'ANCHIETA'
             },
            {'code': '56090',
             'seq': '008',
             'city': 'APIACA'
             },
            {'code': '56111',
             'seq': '009',
             'city': 'ARACRUZ'
             },
            {'code': '56138',
             'seq': '010',
             'city': 'ATILIO VIVACQUA'
             },
            {'code': '56154',
             'seq': '011',
             'city': 'BAIXO GUANDU'
             },
            {'code': '56170',
             'seq': '012',
             'city': 'BARRA DE SAO FRANCISCO'
             },
            {'code': '56197',
             'seq': '013',
             'city': 'BOA ESPERANCA'
             },
            {'code': '56219',
             'seq': '014',
             'city': 'BOM JESUS DO NORTE'
             },
            {'code': '07587',
             'seq': '015',
             'city': 'BREJETUBA'
             },
            {'code': '56235',
             'seq': '016',
             'city': 'CACHOEIRO DE ITAPEMIRIM'
             },
            {'code': '56251',
             'seq': '017',
             'city': 'CARIACICA'
             },
            {'code': '56278',
             'seq': '018',
             'city': 'CASTELO'
             },
            {'code': '56294',
             'seq': '019',
             'city': 'COLATINA'
             },
            {'code': '56316',
             'seq': '020',
             'city': 'CONCEICAO DA BARRA'
             },
            {'code': '56332',
             'seq': '021',
             'city': 'CONCEICAO DO CASTELO'
             },
            {'code': '56359',
             'seq': '022',
             'city': 'DIVINO SAO LOURENCO'
             },
            {'code': '56375',
             'seq': '023',
             'city': 'DOMINGOS MARTINS'
             },
            {'code': '56391',
             'seq': '024',
             'city': 'DORES DO RIO PRETO'
             },
            {'code': '56413',
             'seq': '025',
             'city': 'ECOPORANGA'
             },
            {'code': '56430',
             'seq': '026',
             'city': 'FUNDAO'
             },
            {'code': '11142',
             'seq': '027',
             'city': 'GOVERNADOR LINDEMBERG'
             },
            {'code': '56456',
             'seq': '028',
             'city': 'GUACUI'
             },
            {'code': '56472',
             'seq': '029',
             'city': 'GUARAPARI'
             },
            {'code': '57096',
             'seq': '030',
             'city': 'IBATIBA'
             },
            {'code': '56499',
             'seq': '031',
             'city': 'IBIRACU'
             },
            {'code': '60119',
             'seq': '032',
             'city': 'IBITIRAMA'
             },
            {'code': '56510',
             'seq': '033',
             'city': 'ICONHA'
             },
            {'code': '29319',
             'seq': '034',
             'city': 'IRUPI'
             },
            {'code': '56537',
             'seq': '035',
             'city': 'ITAGUACU'
             },
            {'code': '56553',
             'seq': '036',
             'city': 'ITAPEMIRIM'
             },
            {'code': '56570',
             'seq': '037',
             'city': 'ITARANA'
             },
            {'code': '56596',
             'seq': '038',
             'city': 'IUNA'
             },
            {'code': '57134',
             'seq': '039',
             'city': 'JAGUARE'
             },
            {'code': '56618',
             'seq': '040',
             'city': 'JERONIMO MONTEIRO'
             },
            {'code': '57215',
             'seq': '041',
             'city': 'JOAO NEIVA'
             },
            {'code': '57231',
             'seq': '042',
             'city': 'LARANJA DA TERRA'
             },
            {'code': '56634',
             'seq': '043',
             'city': 'LINHARES'
             },
            {'code': '56650',
             'seq': '044',
             'city': 'MANTENOPOLIS'
             },
            {'code': '07609',
             'seq': '045',
             'city': 'MARATAIZES'
             },
            {'code': '29297',
             'seq': '046',
             'city': 'MARECHAL FLORIANO'
             },
            {'code': '57070',
             'seq': '047',
             'city': 'MARILANDIA'
             },
            {'code': '56677',
             'seq': '048',
             'city': 'MIMOSO DO SUL'
             },
            {'code': '56693',
             'seq': '049',
             'city': 'MONTANHA'
             },
            {'code': '56715',
             'seq': '050',
             'city': 'MUCURICI'
             },
            {'code': '56731',
             'seq': '051',
             'city': 'MUNIZ FREIRE'
             },
            {'code': '56758',
             'seq': '052',
             'city': 'MUQUI'
             },
            {'code': '56774',
             'seq': '053',
             'city': 'NOVA VENECIA'
             },
            {'code': '56790',
             'seq': '054',
             'city': 'PANCAS'
             },
            {'code': '57150',
             'seq': '055',
             'city': 'PEDRO CANARIO'
             },
            {'code': '56812',
             'seq': '056',
             'city': 'PINHEIROS'
             },
            {'code': '56839',
             'seq': '057',
             'city': 'PIUMA'
             },
            {'code': '07625',
             'seq': '058',
             'city': 'PONTO BELO'
             },
            {'code': '56855',
             'seq': '059',
             'city': 'PRESIDENTE KENNEDY'
             },
            {'code': '57118',
             'seq': '060',
             'city': 'RIO BANANAL'
             },
            {'code': '56871',
             'seq': '061',
             'city': 'RIO NOVO DO SUL'
             },
            {'code': '56898',
             'seq': '062',
             'city': 'SANTA LEOPOLDINA'
             },
            {'code': '57258',
             'seq': '063',
             'city': 'SANTA MARIA DE JETIBA'
             },
            {'code': '56910',
             'seq': '064',
             'city': 'SANTA TERESA'
             },
            {'code': '29335',
             'seq': '065',
             'city': 'SAO DOMINGOS DO NORTE'
             },
            {'code': '56936',
             'seq': '066',
             'city': 'SAO GABRIEL DA PALHA'
             },
            {'code': '56952',
             'seq': '067',
             'city': 'SAO JOSE DO CALCADO'
             },
            {'code': '56979',
             'seq': '068',
             'city': 'SAO MATEUS'
             },
            {'code': '07641',
             'seq': '069',
             'city': 'SAO ROQUE DO CANAA'
             },
            {'code': '56995',
             'seq': '070',
             'city': 'SERRA'
             },
            {'code': '07668',
             'seq': '071',
             'city': 'SOORETAMA'
             },
            {'code': '57274',
             'seq': '072',
             'city': 'VARGEM ALTA'
             },
            {'code': '57290',
             'seq': '073',
             'city': 'VENDA NOVA DO IMIGRANTE'
             },
            {'code': '57010',
             'seq': '074',
             'city': 'VIANA'
             },
            {'code': '29351',
             'seq': '075',
             'city': 'VILA PAVAO'
             },
            {'code': '07684',
             'seq': '076',
             'city': 'VILA VALERIO'
             },
            {'code': '57037',
             'seq': '077',
             'city': 'VILA VELHA'
             },
            {'code': '57053',
             'seq': '078',
             'city': 'VITORIA'
             },
            {'code': '57053',
             'seq': '078',
             'city': 'Outros'
             }
        ]
        data = None
        for index, item in enumerate(data_list):
            try:
                if parameter.upper() in str(item['city']):
                    data = item
            except ValueError:
                pass

        return data

    def set_revenue(self, parameter):
        data_list = [
            {'txt_desc_servico': 'Comercialização de Produção Agropecuária Origem Animal - FRSP',
             'txt_hdcdrec': 1740,
             'TXT_SERVICO': "22574",
             },
            {'txt_desc_servico': 'Comercialização de Produção Agropecuária Origem Vegetal - FRSP',
             'txt_hdcdrec': 1570,
             'TXT_SERVICO': "22573",
             },
            {'txt_desc_servico': 'Comercialização de Produção Artesanal - FRSP',
             'txt_hdcdrec': 1201,
             'TXT_SERVICO': "22572",
             },
            {'txt_desc_servico': 'Comercialização de Produção Industrial - FRSP',
             'txt_hdcdrec': 1198,
             'TXT_SERVICO': "22571"
             }
        ]
        data = None
        for index, item in enumerate(data_list):
            try:
                if parameter in str(item['txt_desc_servico']):
                    item['txt_desc_servico'] = item['txt_desc_servico'].replace('çã', '&ccedil;&atilde;').replace('á', '&aacute;')
                    data = item
            except ValueError:
                pass
        return data

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

    dua.emit(
        amount="2,00",
        due_date="20/03/2021",
        cpf_cnpj="12345678909",
        city_name='Cariacica',
        revenue_desc='Comercialização de Produção Industrial - FRSP',
        description='2 Blocos de concreto'
    )

    print('GUARDE ESSE NÚMERO PARA CONSULTA POSTERIOR: ', dua.get_dua_number())

    dua.get_pdf()
    dua.consult(cpf_cnpj=12345678909, nr_dua=dua.get_dua_number())

    # dua.get_pdf(template='3350472976-dua.html', nr_dua='3350472976', native=False)
    # dua.consult(cpf_cnpj=12345678909, nr_dua=3350472976)

    # params = dua.city_params(parameter='pancas')
    # print(params)

    # dua.consult(cpf_cnpj=12345678909, nr_dua=3349043900)
    # dua.consult(cpf_cnpj=12345678909, nr_dua=3348393517)
    # dua.consult(cpf_cnpj=12345678909, nr_dua=3348768340)
    # dua.consult(cpf_cnpj=12345678909, nr_dua=3348804916)
    # json_data = dua.consult(cpf_cnpj=12345678909, nr_dua=3348822906)
    # print(json_data)
