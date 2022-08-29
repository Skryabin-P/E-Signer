
import argparse
import PyPDF2
import re
import sys
import datetime
from cryptography.hazmat import backends
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID
from endesive import pdf
signature_string = lambda organization, date, country : (organization + '\nDATE: '+ date)

def eprint(error):
    print(error, file=sys.stderr)

def load_pfx(file_path, password):
    """ Function to load pkcs12 object from the given password protected pfx file."""

    with open(file_path, 'rb') as fp:
        return pkcs12.load_key_and_certificates(fp.read(), password.encode(), backends.default_backend())



OID_NAMES = {
    NameOID.COMMON_NAME: 'CN',
    NameOID.COUNTRY_NAME: 'C',
    NameOID.DOMAIN_COMPONENT: 'DC',
    NameOID.EMAIL_ADDRESS: 'E',
    NameOID.GIVEN_NAME: 'G',
    NameOID.LOCALITY_NAME: 'L',
    NameOID.ORGANIZATION_NAME: 'O',
    NameOID.ORGANIZATIONAL_UNIT_NAME: 'OU',
    NameOID.SURNAME: 'SN'
}

def get_rdns_names(rdns):
    names = {}
    for oid in OID_NAMES:
        names[OID_NAMES[oid]] = ''
    for rdn in rdns:
        for attr in rdn._attributes:
            if attr.oid in OID_NAMES:
                names[OID_NAMES[attr.oid]] = attr.value
    return names

def run(pfx_certificates, password,input_file, dest, all ):
    try:
        first_time = True
        for pfx_certificate in pfx_certificates:
            # Load the PKCS12 object from the pfx file
            p12pk, p12pc, p12oc = load_pfx(pfx_certificate, password)

            if not first_time:
                input_file = dest
            names = get_rdns_names(p12pc.subject.rdns)
            pdf_f = open(input_file,'rb')
            pdfread = PyPDF2.PdfFileReader(pdf_f)
            num_pages = pdfread.getNumPages()
            pages = num_pages
            start = num_pages - 1
            dest = dest if dest else input_file
            if all:
               start = 0
            for page in range(start,pages):
                if not first_time:
                    input_file = dest
                date = datetime.datetime.now()
                date = date.strftime(f'%Y%m%d%H%M%S+03\'00\'')

                pdf_f = open(input_file, 'rb')
                pdfread = PyPDF2.PdfFileReader(pdf_f)

                fields = pdfread.get_fields()

                if str(type(fields)) != "<class 'NoneType'>":
                    signs = fields.keys()
                else:
                    signs = ['nothing']
                i = 1
                for sign in signs:
                    for t in range(1,4):
                        mask = f"Signature{t}_p{page+1}s"
                        if mask in sign:
                            i+=1




                if i == 1:
                    plus_coord = 0
                else:
                    plus_coord = 150 * (i-1)
                dct = {
                "aligned": 0,
                "sigflags": 3,
                "sigflagsft": 132,
                "sigpage": page,
                'sigandcertify': True,
                "auto_sigfield": False,
                #"sigandcertify": False,
                "signaturebox": (50 + plus_coord, 50, 200 + plus_coord, 125),
                "signform": False,
                "sigfield": f"Signature{i}_p{page + 1}s",
                "signature_appearance": {
                    'background': [1, 1, 1],
                    # 'icon': '../signature_test.png',
                    'outline': [0.2, 0.3, 0.5],
                    'border': 2,
                    'labels': False,
                    'display': 'CN,contact'.split(','),
                    },

                "contact": names['E'],

                "location": "Russia",
                "signingdate": date,
                "reason": "Подписание",
                # "signature": signature,
                "password": password,

                }



                datau = open(input_file, 'rb').read()
                datas = pdf.cms.sign(datau,
                             dct,
                             p12pk, p12pc, p12oc,
                             'sha256'
                             )


                output_file = input_file.replace(input_file, dest)
                with open(output_file, 'wb') as fp:
                  fp.write(datau)
                  fp.write(datas)
                first_time = False
        return True
    except Exception as e:
        import traceback; traceback.print_exc()
        eprint(e)
        return False
        # sys.exit()

if __name__ == '__main__':
    input_file = 'doc2.pdf'
    pfx_certificate = 'container.pfx'
    password = '123'
    dest = 'doc2.pdf'

    print(run(pfx_certificate,password,dest,input_file))
