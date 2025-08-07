#!/usr/bin/env python3

import sys
def eprint(*args, **kwargs): print(*args, file=sys.stderr, **kwargs)
import json

from quetzal_annotator.universal_spectrum_identifier import UniversalSpectrumIdentifier


class UniversalSpectrumIdentifierValidator(object):

    def __init__(self, usi_list=None, options=None):

        self.usi_list = usi_list
        self.options = options

        self.error_code = None
        self.error_message = None
        self.response = { 'error_code': 'OK', 'error_message': '', 'validation_results': {} }

        if usi_list is not None:
            self.validate_usi_list()


    #### Set the error state with supplied information
    def set_error(self, error_code, error_message):
        self.error_code = error_code
        self.error_message = error_message
        self.response['error_code'] = error_code
        self.response['error_message'] = error_message


    #### Parse the USI string
    def validate_usi_list(self, usi_list=None, options=None, verbose=False):

        # Get or set the usi_list and ensure that it is valid
        if usi_list is None:
            usi_list = self.usi_list
        else:
            self.usi_list = usi_list
        if usi_list is None:
            self.set_error("NullUSIList","USI List is NULL")
            return self
        if not isinstance(usi_list, list):
            self.set_error("NotListOfUSIs","The input list of USIs is not a list")
            return self

        # Handle verbose mode
        verboseprint = print if verbose else lambda *a, **k: None
        verboseprint(f"INFO: Validating list of {len(usi_list)} USIs")

        self.response = { 'error_code': 'OK', 'error_message': '', 'validation_results': {} }
        validation_results = self.response['validation_results']

        #### Loop over the list of USIs and validate them
        for usi_str in usi_list:

            #### Check to see if we've already done this one
            if usi_str in validation_results:
                verboseprint(f"INFO: Skipping USI already validated '{usi_str}'")
                continue

            verboseprint(f"INFO: Validating USI '{usi_str}'")

            usi = UniversalSpectrumIdentifier()
            usi.parse(usi_str, verbose=verbose)

            result = usi.__dict__
            validation_results[usi_str] = result

        return self



    def get_example_valid_usi_list(self):
        example_usis = [
            "mzspec:PXD002437:00261_A06_P001564_B00E_A00_R1:scan:10951",
            "mzspec:PXD002437:00261_A06_P001564_B00E_A00_R1:scan:10951:PEPT[Phospho]IDELVISK/2",
            "mzspec:PXD001234:00261_A06_P001564_B00E_A00_R1:index:10951",
            "mzspec:PXD002437:00261_A06_P001564_B00E_A00_R1:scan:10951:PEPT[Phospho]IDELVISK/2",
            "mzspec:PXD002437:00261_A06_P001564_B00E_A00_R1:scan:10951:PEPT[+79]IDELVISK/2",
            "mzspec:PXD002437:00261_A06_P001564_B00E_A00_R1:scan:10951:PEPT[UNIMOD:34]IDELVISK/2",
            "mzspec:PXD001234:Dilution1:4:scan:10951",
            "mzspec:PXD002437:00261_A06_P001564_B00E_A00_R1:test1:scan:10951:PEPT[Phospho]IDELVISK/2",
            "mzspec:PXD002437:00261_A06_P001564_B00E_A00_R1\\:test1:scan:10951:PEPT[Phospho]IDELVISK/2",
            "mzspec:PXD002437:00261_A06_P001564_B00E_A00_R1:scan:10951:PEPT[Phospho]IDELVISK/2:PA-28732",
            "mzspec:PXD001234:[Control]fr10:scan:10951",
            "mzspec:PXD001234:[Control[2]]fr10:scan:10951",
            "mzspec:PXD001234:[Control]fr10[7]:scan:10951",
            "mzspec:PXD001234:[Control[2]]fr10[7]:scan:10951"
        ]
        return example_usis



    def get_example_invalid_usi_list(self):
        example_usis = [
            "PXD002437:00261_A06_P001564_B00E_A00_R1:scan:10951",
            "mzspec:PASS002437:00261_A06_P001564_B00E_A00_R1:scan:10951:PEPT[Phospho]IDELVISK/2",
            None,
            3,
            "mzspec",
            "mzspec:",
            "mzspec:PXD001234",
            "mzspec:PXD001234:00261_A06_P001564_B00E_A00_R1:scan"
        ]
        return example_usis



#### A very simple example of using this class
def example():
    usi_string = "mzspec:PXD000000:a:scan:1:{Hex|INFO:completely labile}[iTRAQ4plex]-EM[Oxidation]EVNESPEK[UNIMOD:214]-[Methyl]/2"
    usi_validator = UniversalSpectrumIdentifierValidator([usi_string])
    print(json.dumps(usi_validator.response,sort_keys=True,indent=2))



#### Direct command-line invocation
def main():
    example()

if __name__ == "__main__": main()
