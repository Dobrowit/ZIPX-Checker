#!/usr/bin/python3

import zipfile
import xml.etree.ElementTree as ET
import os
import sys
import subprocess
from tkinter import filedialog as fd
import pathlib
import tkinter.ttk as ttk
import pygubu

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "zipx-fastview.ui"
ZIPXFILE = ''
TMPDIR = 'C:\\TEMP\\'
ORGAN_WYD = 'Burmistrz Miasta Łeby'
SEPARATOR = '========='

class zfApp:
    def __init__(self, master=None):
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        # Main widget
        self.mainwindow = builder.get_object("toplevel1", master)
        builder.connect_callbacks(self)

        # center window on screen after creation
        self._first_init = True
        self.mainwindow.bind("<Map>", self.center_window)
        
        self.entry_streszczenie = builder.get_object("entry_streszczenie")
        try:
            if len(sys.argv) > 0:
                global ZIPXFILE
                ZIPXFILE = sys.argv[1]
                self.print_zipix_info(ZIPXFILE)
        except:
            pass

    ORGAN_WYD = 'Burmistrza Miasta Łeby'

    def center_window(self, event):
        if self._first_init:
##            print("centering window...")
            toplevel = self.mainwindow
            height = toplevel.winfo_height()
            width = toplevel.winfo_width()
            x_coord = int(toplevel.winfo_screenwidth() / 2 - width / 2)
            y_coord = int(toplevel.winfo_screenheight() / 2 - height / 2)
            geom = f"{width}x{height}+{x_coord}+{y_coord}"
            toplevel.geometry(geom)
            self._first_init = False

    def run(self):
        self.mainwindow.mainloop()

    def print_zipix_info(self, ZFILE):
        error_sw = False
        FILE = ZFILE

    #### akt.xml
        with zipfile.ZipFile(FILE) as myzip:
            with myzip.open('akt.xml') as myfile:
                tree = ET.parse(myfile)
                root = tree.getroot()

        xml_numer = root[0].attrib['numer']
        rodzaj_akt = root[0].attrib['nazwa']
        xml_nazwa = root[0].attrib['opis-typu']
        xml_organ_wydajacy = root[0].attrib['organ-wydajacy-m']
        xml_status_aktu = root[0].attrib['status-aktu']

        # blok = 'brak blokad'
        # if 'zablokowany' in root.attrib:
        #     if (root.attrib['zablokowany'] == 'tak'):
        #         blok = 'zablokowany'

        try:
            signed = root.find('.//{http://www.w3.org/2000/09/xmldsig#}KeyName').text
            blok = 'zablok-cert'
        except:
            signed = "## BRAK PODPISU! ##"

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
            rodzaj_meta = root.find('.//{http://www.mswia.gov.pl/standardy/ndap}typ/{http://www.mswia.gov.pl/standardy/ndap}rodzaj').text
        except:
            rodzaj_meta = "?"

        myfile.close()

    #### mark.xml
        with zipfile.ZipFile(FILE) as myzip:
            with myzip.open('Properties/mark.xml') as myfile:
                tree = ET.parse(myfile)
                root = tree.getroot()
        
        try:
            keywordsy = root.find('.//{http://zipx.org.pl/mark.xsd}Keywords')
            if keywordsy == None:
                keywordsy = '## BRAK SŁÓW KLUCZOWYCH! ##'
            else:
                keywordsy = 'OK'
        except:
            keywordsy = "?"

        try:
            isfrozen = root.find('.//{http://zipx.org.pl/mark.xsd}IsFrozen').text
            if isfrozen == 'true':
                blok = 'zablokowany'
            else:
                blok = '## BRAK BLOKAD! ##'
        except:
            pass
        
##        print("Nazwa pliku:", FILE)
##        print(SEPARATOR)
##        print("Numer aktu:", xml_numer)
##        print("Rodzaj:", xml_nazwa)
##        print("Organ wydający:", xml_organ_wydajacy)
        if  rodzaj_akt == rodzaj_meta:
            zam = 'OK'
        else:
            zam = 'Brak zgodności!'
##        print("\nZgodność rodzaju akt z metadanymi:", zam)
##        print("Słowa kluczowe:", keywordsy)
##        print("\nAutor:", autor)
##        print("Blokada:", blok)
##        print("Status:", xml_status_aktu)
##        print("Podpis:", signed)
##        print("")
##        print(wsprawie)
##        print(SEPARATOR)

        self.builder.tkvariables['var_entry_nraktu'].set(xml_numer)
        self.builder.tkvariables['var_entry_rodzaj'].set(xml_nazwa)
        self.builder.tkvariables['var_entry_organwydajacy'].set(xml_organ_wydajacy)
        self.builder.tkvariables['var_entry_poprawnosc'].set(zam)
        self.builder.tkvariables['var_entry_slowakluczowe'].set(keywordsy)
        self.builder.tkvariables['var_entry_autor'].set(autor)
        self.builder.tkvariables['var_entry_blokada'].set(blok)
        self.builder.tkvariables['var_entry_status'].set(xml_status_aktu)
        self.builder.tkvariables['var_entry_podpis'].set(signed)
        txt = self.entry_streszczenie
        txt.config(state="normal")
        txt.delete("1.0","end")
        txt.insert("end", wsprawie + "\n")
        txt.config(state="disabled")

    ## wykrywanie błędów
        if wsprawie.find('  ') != -1:
##            print(MYERROR, "zdublowane spacje w tytule", wsprawie.find('  '))
            error_sw = True

        if xml_organ_wydajacy != ORGAN_WYD:
##            print(MYERROR, "błędny organ wydający")
            error_sw = True

        if (' ' in xml_numer) == True:
##            print(MYERROR, "błędny numer (spcje)")
            error_sw = True

        if any(c.isalpha() for c in xml_numer):
##            print(MYERROR, "błędny numer (litery)")
            error_sw = True

        if xml_numer[-5] != '/':
##            print(MYERROR, "błędny numer (separator)")
            error_sw = True

        if keywordsy != 'OK':
##            print(MYERROR, "brak słów kluczowych")
            error_sw = True

        if blok == 'brak blokad':
##            print(MYERROR, "brak blokady")
            error_sw = True

        if error_sw:
            self.builder.tkvariables['var_entry_poprawnosc'].set("WYSTĄPIŁY INNE BŁĘDY!")

    def button_press_load(self, event=None):
        try:
            global ZIPXFILE
            ZIPXFILE = fd.askopenfilename()
            self.print_zipix_info(ZIPXFILE)
        except:
            pass

    def button_press_showpdf(self, event=None):
        try:
            with zipfile.ZipFile(ZIPXFILE, 'r') as zipObject:
               listOfFileNames = zipObject.namelist()
               zipObject.extract('akt.pdf', TMPDIR)
            PDFFILE = TMPDIR + 'akt.pdf'
            subprocess.Popen([PDFFILE], shell=True)
        except:
            pass           

    def button_press_keywords(self, event=None):
        def extract_keywords(element, level=0):
            keywords = []
            namespace = {'ns': 'http://zipx.org.pl/mark.xsd'}
            for item in element.findall('.//ns:Item', namespace):
                text = item.find('ns:Text', namespace)
                if text is not None:
                    keywords.append((level, text.text))
                keywords.extend(extract_keywords(item, level + 1))
            return keywords

        # Wczytaj plik XML
        print(ZIPXFILE)
        with zipfile.ZipFile(ZIPXFILE) as myzip:
            with myzip.open('Properties/mark.xml') as myfile:
                tree = ET.parse(myfile)
                root = tree.getroot()

        # Znajdź element Keywords
        namespace = {'ns': 'http://zipx.org.pl/mark.xsd'}
        keywords_element = root.find('.//ns:Keywords', namespace)

        if keywords_element is not None:
            # Wyodrębnij słowa kluczowe
            all_keywords = extract_keywords(keywords_element)

            # Wypisz słowa kluczowe na konsoli
            for level, keyword in all_keywords:
                print('  ' * level + keyword)
        else:
            print("Nie znaleziono elementu Keywords w pliku XML.")

if __name__ == "__main__":
    app = zfApp()
    app.run()


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
