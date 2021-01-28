# _pydua_

PYDUA is a python library that facilitates the emission, consult and generation PDF of the "Single Tax Revenues Document" of ES-Brazil .

# Installing the pydua library

```pip install git+https://github.com/cleitonleonel/pydua.git```

# How to use

```python
from api import DuaAPI

dua = DuaAPI()
dua.emit(
    amount="2,00",
    due_date="27/01/2021",
    cpf_cnpj="12345678909",
    city_name='Cariacica',
    revenue_desc='Comercialização de Produção Industrial - FRSP',
    description='Teste de emissão de DUA eletrônico'
)
number = dua.get_dua_number()
consult = dua.consult(cpf_cnpj=12345678909, nr_dua=number)
pdf = dua.get_pdf()
```

# Did this lib help you?

If this lib lets you feel free to make a donation =), it can be R $ 0.50 hahahaha. To do so, just read the qrcode below, it was generated with the lib sample file.

![QRCode Doação](https://github.com/cleitonleonel/pypix/blob/master/qrcode.png?raw=true)


# Author

Cleiton Leonel Creton ==> cleiton.leonel@gmail.com