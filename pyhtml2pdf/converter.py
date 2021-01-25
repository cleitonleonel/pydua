import os
import json
import base64
import logging
import shutil

from selenium import webdriver
from selenium.webdriver.remote.remote_connection import LOGGER

LOGGER.setLevel(logging.WARNING)
from urllib3.connectionpool import log

log.setLevel(logging.WARNING)
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of
from webdriver_manager.chrome import ChromeDriverManager

from .compressor import __compress


def convert(driver_path: str, source: str, target: str, timeout: int = 2, compress: bool = False, power: int = 0, install_driver: bool = False):
    """
    Convert a given html file or website into PDF

    :param driver_path:
    :param install_driver:
    :param str source: source html file or website link
    :param str target: target location to save the PDF
    :param int timeout: timeout in seconds. Default value is set to 2 seconds
    :param bool compress: whether PDF is compressed or not. Default value is False
    :param int power: power of the compression. Default value is 0. This can be 0: default, 1: prepress, 2: printer, 3: ebook, 4: screen
   """

    result = __get_pdf_from_html(driver_path, source, timeout, install_driver)

    if compress:
        __compress(result, target, power)
    else:
        with open(target, 'wb') as file:
            file.write(result)

    return result


def __send_devtools(driver, cmd, params={}):
    resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
    url = driver.command_executor._url + resource
    body = json.dumps({'cmd': cmd, 'params': params})
    response = driver.command_executor._request('POST', url, body)

    if not response:
        raise Exception(response.get('value'))

    return response.get('value')


def manager_path_binary(binary_path):
    new_binary = os.path.join('bin/', os.path.basename(binary_path))
    shutil.copyfile(binary_path, new_binary)
    os.chmod(new_binary, 0o755)
    shutil.rmtree('bin/drivers')
    os.remove('bin/drivers.json')
    return new_binary


def __get_pdf_from_html(driver_path: str, path: str, timeout: int, install_driver: bool, print_options={}):
    webdriver_options = Options()
    webdriver_prefs = {}
    driver = None

    webdriver_options.add_argument('--headless')
    webdriver_options.add_argument('--disable-gpu')
    webdriver_options.add_argument('--no-sandbox')
    webdriver_options.add_argument('--disable-dev-shm-usage')
    webdriver_options.experimental_options['prefs'] = webdriver_prefs

    webdriver_prefs['profile.default_content_settings'] = {'images': 2}

    if install_driver:
        download_path = ChromeDriverManager(path='bin').install()
        binary = manager_path_binary(download_path)
        driver = webdriver.Chrome(binary, options=webdriver_options)
    else:
        try:
            driver = webdriver.Chrome(driver_path, options=webdriver_options)
        except:
            download_path = ChromeDriverManager(path='bin').install()
            binary = manager_path_binary(download_path)
            driver = webdriver.Chrome(binary, options=webdriver_options)

    driver.get(path)

    try:
        WebDriverWait(driver, timeout).until(staleness_of(driver.find_element_by_tag_name('html')))
    except TimeoutException:
        calculated_print_options = {
            'landscape': False,
            'displayHeaderFooter': False,
            'printBackground': True,
            'preferCSSPageSize': True,
        }
        calculated_print_options.update(print_options)
        result = __send_devtools(driver, "Page.printToPDF", calculated_print_options)
        driver.quit()
        return base64.b64decode(result['data'])
