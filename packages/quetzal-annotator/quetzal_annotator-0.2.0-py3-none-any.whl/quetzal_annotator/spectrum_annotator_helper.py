#!/usr/bin/env python3
import sys
import argparse
def eprint(*args, **kwargs): print(*args, file=sys.stderr, **kwargs)

from quetzal_annotator.spectrum import Spectrum

DEBUG = False


####################################################################################################
#### SpectrumAnnotatorHelper class
class SpectrumAnnotatorHelper:
    '''
    - get_isobaric_labeling_mode()                Determine the most appropriate isobaric_labeling_mode based on user input
    '''

    ####################################################################################################
    #### Constructor
    def __init__(self):
        pass


    ####################################################################################################
    #### Identify known reporter ions, somewhat independently of whether they should be there or not
    def get_isobaric_labeling_mode(self, spectrum):

        #### Try to get the user value from spectrum object
        try:
            isobaric_labeling_mode = spectrum.extended_data['user_parameters']['isobaric_labeling_mode']
        except:
            isobaric_labeling_mode = 'automatic'
        if not isinstance(isobaric_labeling_mode, str):
            isobaric_labeling_mode = 'automatic'

        #### Define allowed values
        allowed_values = [ 'automatic', 'TMT', 'iTRAQ', 'none' ]
 
        #### Try to determine the user selection in a case-insensitive way
        found_match = False
        for allowed_value in allowed_values:
            if isobaric_labeling_mode.upper() == allowed_value.upper():
                isobaric_labeling_mode = allowed_value
                found_match = True

        #### Or just assign 'automatic' if we cannot figure it out
        if not found_match:
            isobaric_labeling_mode = 'automatic'

        return isobaric_labeling_mode



####################################################################################################
#### For command-line usage
def main():

    argparser = argparse.ArgumentParser(description='Class representing a peptidoform')
    argparser.add_argument('--verbose', action='count', help='If set, print more information about ongoing processing' )
    argparser.add_argument('--isobaric_labeling_mode', action='store', default='automatic', type=str, help='Set the isobaric labeling mode, one of [automatic|TMT|iTRAQ|none]' )
    params = argparser.parse_args()

    # Set verbose mode
    verbose = params.verbose
    if verbose is None:
        verbose = 0

    self = SpectrumAnnotatorHelper()

    #### Fetch the spectrum
    spectrum = Spectrum()
    spectrum.extended_data['user_parameters'] = {}

    spectrum.extended_data['user_parameters']['isobaric_labeling_mode'] = params.isobaric_labeling_mode
    isobaric_labeling_mode = self.get_isobaric_labeling_mode(spectrum)
    print(f"isobaric_labeling_mode={isobaric_labeling_mode}")

#### For command line usage
if __name__ == "__main__": main()
