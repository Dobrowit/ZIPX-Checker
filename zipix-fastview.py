import zipfile
import xml.etree.ElementTree as ET
import os
import sys
import subprocess

ZIPXFILE = 'D:\\DOKUMENTY\\#_Akty_prawne\\Zarzadzenia_Burmistrza\\robocze\\zarzadzenie-218.zipx'
TMPDIR = 'D:\\DOKUMENTY\\#_Akty_prawne\\Zarzadzenia_Burmistrza\\robocze\\'
ORGAN_WYD = 'Burmistrza Miasta Łeby'
MYERROR = '######## BŁĄD!!! ##'
SEPARATOR = '========='

def print_zipix_info(FILE):
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

    
    print("Nazwa pliku:", FILE)
    print(SEPARATOR)
    print("Numer aktu:", xml_numer)
    print("Rodzaj:", rodzaj, xml_nazwa)
    print("Organ wydający:", xml_organ_wydajacy)
    print("Słowa kluczowe:", keywordsy)
    print("Autor:", autor)
    print("Blokada:", blok)
    print("Status:", xml_status_aktu)
    print("Podpis:", signed)
    print("")
    print(wsprawie)
    print(SEPARATOR)
    
## wykrywanie błędów
    if wsprawie.find('  ') != -1:
        print(MYERROR, "zdublowane spacje w tytule", wsprawie.find('  '))
        error_sw = True

    if xml_organ_wydajacy != ORGAN_WYD:
        print(MYERROR, "błędny organ wydający")
        error_sw = True

    if (' ' in xml_numer) == True:
        print(MYERROR, "błędny numer (spcje)")
        error_sw = True

    if any(c.isalpha() for c in xml_numer):
        print(MYERROR, "błędny numer (litery)")
        error_sw = True

    if xml_numer[-5] != '/':
        print(MYERROR, "błędny numer (separator)")
        error_sw = True

    if keywordsy != 'keyok':
        print(MYERROR, "brak słów kluczowych")
        error_sw = True

    if blok == 'brak blokad':
        print(MYERROR, "brak blokady")
        error_sw = True

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

if len(sys.argv) > 0:
    ZIPXFILE = sys.argv[1]
    print_zipix_info(ZIPXFILE)

    try:
        with zipfile.ZipFile(ZIPXFILE, 'r') as zipObject:
           listOfFileNames = zipObject.namelist()
           zipObject.extract('akt.pdf', TMPDIR)
        PDFFILE = TMPDIR + 'akt.pdf'
        subprocess.Popen([PDFFILE], shell=True)
    except:
        print("BRAK BLOKADY LUB PODPISU ORAZ WIZUALIZACJI PDF!")
else:
    print('BRAK PLIKU...')


##print_zipix_info(TMPDIR + 'Zarządzenie.5.2022-01-10.zipx')
##
##try:
##    input("Press enter to continue")
##except SyntaxError:
##    pass

#os.system("pause")
