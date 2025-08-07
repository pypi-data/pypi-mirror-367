#!/usr/bin/env python3

import sys
import os
import argparse
import os.path
import re
import json
import numpy
import urllib.parse
import requests
import requests_cache
def eprint(*args, **kwargs): print(*args, file=sys.stderr, **kwargs)


####################################################################################################
#### SpectrumFetcher class
class SpectrumFetcher:

    #### Constructor
    def __init__(self, attribute_list=None, peak_list=None, analyte_list=None):
        """
        __init__ - SpectrumFetcher constructor

        Parameters
        ----------
        attribute_list: list
            A list of attribute [key, value (, group)] sets to initialize to.
        """

        self.peak_list = []
        self.attributes = {}
        self.precursor_mz = 0.0
        self.precursor_charge = 1
        self.precursor_neutral_mass = 0.0
        self.usi_string = None

        self.proxi_spectrum = None
        self.proxi_spectra = []

        self.spectrum_counter = 1


    ####################################################################################################
    #### Fetch a list of spectra
    def fetch_spectra(self, usi_list=None, output_format='MGF', output_filename=None):

        if output_format is not None and output_format.upper() == 'MGF' and output_filename is not None:
            outfile = open(output_filename,'w')

        n_fetched_spectra = 0
        for usi_string in usi_list:
            print(f"INFO: Fetching spectrum {self.spectrum_counter} via USI {usi_string}")
            result = self.fetch_spectrum(usi_string)
            if result is None:
                continue

            buffer = self.serialize_spectrum(output_format=output_format)
            if output_format is not None and output_format.upper() == 'MGF':
                if output_filename is None:
                    print(buffer)
                else:
                    outfile.write(buffer)

            n_fetched_spectra += 1

        eprint(f"INFO: {n_fetched_spectra} of {len(usi_list)} spectra fetched")

        if output_format is not None and output_format.upper() == 'MGF' and output_filename is not None:
            outfile.close()

        if output_format is not None and output_format.upper() == 'JSON':
            if output_filename is not None:
                with open(output_filename) as outfile:
                    print(json.dumps(self.proxi_spectra, indent=2, sort_keys=True), file=outfile)
            else:
                print(json.dumps(self.proxi_spectra, indent=2, sort_keys=True))

    ####################################################################################################
    #### Fetch a spectrum from PeptideAtlas given a USI
    def fetch_spectrum(self, usi_string, verbose=1):

        requests_cache.install_cache('spectrum_fetcher.cache.sqlite')

        sources_to_try = [ 'overide', 'ProteomeCentral', 'PRIDE', 'PeptideAtlas', 'MassIVE' ]
        urls_to_try = {
            'PRIDE': f"https://www.ebi.ac.uk/pride/proxi/archive/v0.1/spectra?resultType=full&usi={urllib.parse.quote_plus(usi_string)}",
            'ProteomeCentral': f"https://proteomecentral.proteomexchange.org/api/proxi/v0.1/spectra?resultType=full&usi={urllib.parse.quote_plus(usi_string)}",
            'PeptideAtlas': f"https://peptideatlas.org/api/proxi/v0.1/spectra?resultType=full&usi={urllib.parse.quote_plus(usi_string)}",
            'MassIVE': f"https://massive.ucsd.edu/ProteoSAFe/proxi/v0.1/spectra?resultType=full&usi={urllib.parse.quote_plus(usi_string)}"
        }

        # If the USI string is already a URL, then just try to use that
        if usi_string.startswith('http'):
            urls_to_try = { 'overide': usi_string }

        status_code = 0
        for source in sources_to_try:
            if source not in urls_to_try:
                continue
            url = urls_to_try[source]
            if verbose:
                eprint(f"  - Trying {source}")
            response_content = requests.get(url)
            status_code = response_content.status_code
            if status_code != 200:
                if verbose:
                    eprint(f"    {source} returned {status_code}")
            else:
                break
        if status_code != 200:
            eprint(f"ERROR: Unable to fetch spectrum from any of {sources_to_try}")
            return

        proxi_spectrum = response_content.json()
        self.proxi_spectrum = proxi_spectrum[0]
        self.proxi_spectra.append(self.proxi_spectrum)

        self.peak_list = []
        n_peaks = len(proxi_spectrum[0]['mzs'])
        eprint(f"    {source} provided the spectrum with {n_peaks} peaks")

        for i_peak in range(n_peaks):

            # mz should always be there
            mz = float(proxi_spectrum[0]['mzs'][i_peak])

            # Extract the intensity value for the peak if present
            intensity = 1.0
            if 'intensities' in proxi_spectrum[0]:
                intensity = float(proxi_spectrum[0]['intensities'][i_peak])

            # Extract the interpretation_string value for the peak if present
            interpretation_string = '?'
            if 'interpretations' in proxi_spectrum[0] and proxi_spectrum[0]['interpretations'] is not None:
                interpretation_string = proxi_spectrum[0]['interpretations'][i_peak]

            # Store the peak data as a data list in the peak_list
            self.peak_list.append( [ mz, intensity, interpretation_string ] )

        # Extract the attribute list from the fetched JSON
        self.attribute_list = []
        if 'attributes' in proxi_spectrum[0]:
            for attribute in proxi_spectrum[0]['attributes']:
                if attribute['accession'] == 'MS:1000827' or attribute['name'] == 'isolation window target m/z':
                    self.precursor_mz = float(attribute['value'])
                if attribute['accession'] == 'MS:1000744' or attribute['name'] == 'selected ion m/z':
                    self.precursor_mz = float(attribute['value'])
                if attribute['accession'] == 'MS:1000041' or attribute['name'] == 'charge state':
                    self.precursor_charge = int(attribute['value'])

        self.precursor_neutral_mass = 0.0
        if self.precursor_mz and self.precursor_charge:
            self.precursor_neutral_mass = self.precursor_mz * self.precursor_charge
            self.precursor_neutral_mass -= 1.00727646688 * self.precursor_charge

        self.usi_string = usi_string

        return self


    ####################################################################################################
    #### Write a spectrum in the specified format
    def serialize_spectrum(self, output_format='MGF'):

        buffer = ''

        # if the format is MGF, then write an MGF entry
        if output_format is not None and output_format.upper() == 'MGF':
            # Write a terse spectrum header
            buffer += f"BEGIN IONS\n"
            buffer += f"TITLE=Spectrum {self.spectrum_counter}\n"
            self.spectrum_counter += 1
            buffer += f"PRECURSOR={self.precursor_mz}\n"
            buffer += f"PEPMASS={self.precursor_neutral_mass}\n"
            buffer += f"CHARGE={self.precursor_charge}+\n"
            buffer += f"COM={self.usi_string}+\n"
            # Print the peaks
            for peak in self.peak_list:
                buffer += f"{peak[0]}\t{peak[1]}\n"
            buffer += f"END IONS\n\n"

        # if the format is JSON, then write a PROXI-formatted JSON entry
        if output_format is not None and output_format.upper() == 'JSON':
            buffer = json.dumps(self.proxi_spectrum, indent=2, sort_keys=True)

        return buffer


####################################################################################################
#### For command-line usage
def main():

    argparser = argparse.ArgumentParser(description='Utility to fetch spectra via USIs')
    argparser.add_argument('--verbose', action='count', help='If set, print more information about ongoing processing' )
    argparser.add_argument('--usi', action='store', default=None, type=str, help='Single input USI')
    argparser.add_argument('--test', action='count', help='If set, just use an example USI to test')
    argparser.add_argument('--input_filename', action='store', default=None, type=str, help='Filename of input text file of USIs')
    argparser.add_argument('--output_filename', action='store', default=None, type=str, help='Filename of output spectra')
    argparser.add_argument('--output_format', action='store', default=None, type=str, help='Format of output (one of: MGF)')
    params = argparser.parse_args()

    # Set verbose mode
    verbose = params.verbose
    if verbose is None:
        verbose = 1

    # If --example is supplied, then set an example
    usi = None
    if params.test is not None:
        usi = 'mzspec:PXD007058:SF_200217_pPeptideLibrary_pool1_HCDOT_rep1:scan:4336:GQEY[Phospho]LILEK/2'
        if verbose:
            eprint(f"INFO: Using special test USI '{usi}'")

    # If there is a supplied USI, use that
    if params.usi is not None and len(params.usi) > 0:
        usi = params.usi

    # Cursory check
    if usi is not None and not usi.startswith('mzspec:'):
        eprint(f"ERROR: --usi value does not begin with 'mzspec:'. Not a valid USI")
        return

    # Cursory check
    if params.output_format is None:
        eprint(f"INFO: Setting output_format to MGF as a default")
        params.output_format = 'MGF'


    # If there is a supplied input_file, use that
    usi_list = []
    if params.input_filename is not None and len(params.input_filename) > 0:
        if os.path.exists(params.input_filename):
            if verbose:
                eprint(f"INFO: Reading file '{params.input_filename}'")
            with open(params.input_filename) as infile:
                for line in infile:
                    line = line.strip()
                    if line.startswith('mzspec:'):
                        usi_list.append(line)
                    else:
                        if verbose:
                            eprint(f"INFO: Skipping input file line '{line}'")
        else:
            eprint(f"ERROR: Specific input file '{params.input_filename}' not found")
            return

    if len(usi_list) == 0:
        if usi is None:
            eprint(f"ERROR: No --usi value or valid USIs in --input_file. Nothing to do. Use --help for calling assistance")
            return
        usi_list.append(usi)

    if verbose:
        eprint(f"INFO: Fetching spectra for {len(usi_list)} USIs")

    spectrum_fetcher = SpectrumFetcher()
    spectrum_fetcher.fetch_spectra(usi_list=usi_list, output_format=params.output_format, output_filename=params.output_filename)


#### For command line usage
if __name__ == "__main__": main()
