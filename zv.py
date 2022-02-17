import zipfile
import xml.etree.ElementTree as ET
import os

VERBOSE = 1
MYDIRECTORY = 'D:\\DOKUMENTY\\#_Akty_prawne\\Zarzadzenia_Burmistrza\\2021'
ORGAN_WYD = 'Burmistrza Miasta Łeby'
RODZAJ_OK = 'Zarządzenie'
XMLNAZWA = 'zarzadzenie'
MYERROR = '######## BŁĄD!!! ##'
SEPARATOR = '=========\n'

os.chdir(MYDIRECTORY)
dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = os.getcwd()
arr = os.listdir()
errory = 0

print(dir_path)

def print_zipix_info(FILE):
    global errory
    error_sw = False

#### akt.xml
    with zipfile.ZipFile(FILE) as myzip:
        with myzip.open('akt.xml') as myfile:
            tree = ET.parse(myfile)
            root = tree.getroot()

    xml_numer = root[0].attrib['numer']
    xml_nazwa = root[0].attrib['nazwa']
    xml_organ_wydajacy = root[0].attrib['organ-wydajacy']
    xml_status_aktu = root[0].attrib['status-aktu']

    # blok = 'brak blokad'
    # if 'zablokowany' in root.attrib:
    #     if (root.attrib['zablokowany'] == 'tak'):
    #         blok = 'zablokowany'

    try:
        signed = root.find('.//{http://www.w3.org/2000/09/xmldsig#}KeyName').text
        blok = 'zablok-cert'
    except:
        signed = "N/A"

    myfile.close()

#### metadane.xml
    with zipfile.ZipFile(FILE) as myzip:
        with myzip.open('metadane.xml') as myfile:
            tree = ET.parse(myfile)
            root = tree.getroot()
    
    try:
        autor = root.find('.//{http://www.mswia.gov.pl/standardy/ndap}nazwisko').text
    except:
        autor = "?"

    try:
        wsprawie = root.find('.//{http://www.mswia.gov.pl/standardy/ndap}oryginalny').text
    except:
        wsprawie = "?"

    try:
        rodzaj = root.find('.//{http://www.mswia.gov.pl/standardy/ndap}typ/{http://www.mswia.gov.pl/standardy/ndap}rodzaj').text
    except:
        rodzaj = "?"

    myfile.close()

#### mark.xml
    with zipfile.ZipFile(FILE) as myzip:
        with myzip.open('Properties/mark.xml') as myfile:
            tree = ET.parse(myfile)
            root = tree.getroot()
    
    try:
        keywordsy = root.find('.//{http://zipx.org.pl/mark.xsd}Keywords')
        if keywordsy == None:
            keywordsy = 'NOKEY'
        else:
            keywordsy = 'keyok'
    except:
        keywordsy = "?"

    try:
        isfrozen = root.find('.//{http://zipx.org.pl/mark.xsd}IsFrozen').text
        if isfrozen == 'true':
            blok = 'zablokowany'
        else:
            blok = 'brak_blokad'
    except:
        print('?')

    # try:
    #     issigned = root.find('.//{http://zipx.org.pl/mark.xsd}IsSigned').text
    #     print(issigned)
    # except:
    #     print('?')

    if VERBOSE == 2:
        print(FILE, rodzaj, xml_numer, xml_nazwa, xml_organ_wydajacy, blok, xml_status_aktu, keywordsy, autor, signed, sep=" | ")

    if VERBOSE == 3:
        print(wsprawie)
        print(FILE, rodzaj, xml_numer, xml_nazwa, xml_organ_wydajacy, blok, xml_status_aktu, keywordsy, autor, signed, sep=" | ")

#### wykrywanie błędów
##    if wsprawie.find('  ') != -1:
##        print(MYERROR, "zdublowane spacje w tytule", wsprawie.find('  '))
##        errory += 1
##        error_sw = True

    if xml_organ_wydajacy != ORGAN_WYD:
        print(MYERROR, "błędny organ wydający")
        errory += 1
        error_sw = True

    if (' ' in xml_numer) == True:
        print(MYERROR, "błędny numer (spcje)")
        errory += 1
        error_sw = True

    if any(c.isalpha() for c in xml_numer):
        print(MYERROR, "błędny numer (litery)")
        errory += 1
        error_sw = True

    if xml_numer[-5] != '/':
        print(MYERROR, "błędny numer (separator)")
        errory += 1
        error_sw = True

    if keywordsy != 'keyok':
        print(MYERROR, "brak słów kluczowych")
        errory += 1
        error_sw = True

    if blok == 'brak blokad':
        print(MYERROR, "brak blokady")
        errory += 1
        error_sw = True

##    if rodzaj != RODZAJ_OK:
##        print(MYERROR, 'błędny rodzaj dokumentu')
##        errory += 1
##        error_sw = True
        
##    if rodzaj != XMLNAZWA:
##        print(MYERROR, 'błędny rodzaj dokumentu')
##        errory += 1
##        error_sw = True
        
    if VERBOSE == 1:
        if error_sw == True:
            print(wsprawie)
            print(FILE, rodzaj, xml_numer, xml_nazwa, xml_organ_wydajacy, blok, xml_status_aktu, keywordsy, autor, signed, sep=" | ")
            print(SEPARATOR)
            error_sw = False

    if VERBOSE == 2 or VERBOSE == 3:
        if error_sw == True:
            print(SEPARATOR)

# FILE - sprawdzany plik
# rodzaj - rodzaj dokumentu - np. zarządzenie uchwała itp. - wg metadanych (metadane.xml)
# xml_numer - numer aktu; powinien być baz spacji wg schematu nr/rok
# xml_nazwa - tak jak rodzaj - wg matryki w dok. głównym (akt.xml)
# xml_organ_wydajacy - w przypadku zarządzenia burmistrz, w przypadku uchwały przewodniczący
# blok - informacja o blokadzie
# xml_status_aktu - status - dla zarządzenia "przyjęty" dla uchwały "uchwalony"
# keywordsy - sprawdza czy ustalono słownik słów kluczowych
# autor - pierwszy autor dokumentu
# signed - osoba która podpisała dokument cert. kwal.
# wsprawie - pełny tytuł dokumentu - typ, numer oraz 'w sprawie'



for fn in arr:
    if fn[-5:]=='.zipx':
        print_zipix_info(fn)

if errory == 1:
    print(f'Wykryto {errory} błąd.')
elif errory > 1 and errory < 5:
    print(f'Wykryto {errory} błędy.')
elif errory > 4:
    print(f'Wykryto {errory} błędów!')
elif errory == 0:
    print('Brak błędów :-)')
