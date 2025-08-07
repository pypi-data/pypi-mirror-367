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
import timeit
import matplotlib.pyplot as plt
import math

def eprint(*args, **kwargs): print(*args, file=sys.stderr, **kwargs)

from quetzal_annotator.spectrum import Spectrum
from quetzal_annotator.spectrum_annotator import SpectrumAnnotator
from quetzal_annotator.proforma_peptidoform import ProformaPeptidoform
from quetzal_annotator.universal_spectrum_identifier import UniversalSpectrumIdentifier


# Define column offsets for peak_list. This dict-like behavior is a bit more efficient than using actual dicts
PL_I_PEAK = 0
PL_MZ = 1
PL_INTENSITY = 2
PL_INTERPRETATION_STRING = 3
PL_AGGREGATION_INFO = 4
PL_INTERPRETATIONS = 5
PL_ATTRIBUTES = 6



####################################################################################################
#### SpectrumComparator class
class SpectrumComparator:

    #### Constructor
    def __init__(self):
        """
        __init__ - SpectrumComparator constructor

        Parameters
        ----------
        none
        """

        self.target_spectrum = None
        self.reference_spectrum = None
        self.comparison_results = {}



    ####################################################################################################
    #### Compare two spectra with USIs as input
    def compare_usis(self, reference_spectrum_usi=None, target_spectrum_usi=None, tolerance=None, verbose=None):

        if target_spectrum_usi is None:
            eprint(f"ERROR: [compare_usis] target_spectrum_usi must be provided, but is None")
            return
        if reference_spectrum_usi is None:
            eprint(f"ERROR: [compare_usis] reference_spectrum_usi must be provided, but is None")
            return
        if verbose is None:
            verbose = 0

        # Fetch the reference spectrum
        t0 = timeit.default_timer()
        reference_spectrum = Spectrum()
        if reference_spectrum.fetch_spectrum(reference_spectrum_usi) is None:
            print(f"ERROR: Unable to fetch reference spectrum {reference_spectrum_usi}")
            return
        #print(reference_spectrum.show())
        t1 = timeit.default_timer()
        if verbose:
            print(f"INFO: Fetched reference spectrum in {t1-t0:.4f} seconds")

        # Fetch the target spectrum
        t0 = timeit.default_timer()
        target_spectrum = Spectrum()
        if target_spectrum.fetch_spectrum(target_spectrum_usi) is None:
            print(f"ERROR: Unable to fetch target spectrum {target_spectrum_usi}")
            return
        #print(target_spectrum.show())
        t1 = timeit.default_timer()
        if verbose:
            print(f"INFO: Fetched target spectrum in {t1-t0:.4f} seconds")

        comparison_scores = self.compare_spectra(reference_spectrum=reference_spectrum, reference_spectrum_usi=reference_spectrum_usi, target_spectrum=target_spectrum, target_spectrum_usi=target_spectrum_usi, tolerance=tolerance, verbose=verbose)

        return comparison_scores



    ####################################################################################################
    #### Compare two spectrum objects with their USI objects as input
    def compare_spectra(self, reference_spectrum=None, reference_spectrum_usi=None, target_spectrum=None, target_spectrum_usi=None, tolerance=None, verbose=None):

        if target_spectrum_usi is None:
            eprint(f"ERROR: [compare_usis] target_spectrum_usi must be provided, but is None")
            return
        if reference_spectrum_usi is None:
            eprint(f"ERROR: [compare_usis] reference_spectrum_usi must be provided, but is None")
            return

        if target_spectrum is None:
            target_spectrum = Spectrum()
            target_spectrum.fetch_spectrum(target_spectrum_usi)
            #eprint(f"ERROR: [compare_usis] target_spectrum must be provided, but is None")
            #return
        if reference_spectrum is None:
            reference_spectrum = Spectrum()
            reference_spectrum.fetch_spectrum(reference_spectrum_usi)
            #eprint(f"ERROR: [compare_usis] reference_spectrum must be provided, but is None")
            #return
        if verbose is None:
            verbose = 0


        # Annotate the reference spectrum
        self.annotate_spectrum(spectrum=reference_spectrum, spectrum_usi=reference_spectrum_usi, tolerance=tolerance, verbose=verbose)

        # Annotate the target spectrum
        self.annotate_spectrum(spectrum=target_spectrum, spectrum_usi=target_spectrum_usi, tolerance=tolerance, verbose=verbose)

        # MS2PIP only does charge 1+ fragments, so skip the 2+ if MS2PIP included in comparison
        include_charge_two = True
        if 'MS2PIP' in reference_spectrum_usi or 'MS2PIP' in target_spectrum_usi:
            include_charge_two = False

        # Create a list of ions to compare
        comparison_ions = {}

        self.fill_comparison_ions(comparison_ions, target_spectrum, 'target', include_charge_two=include_charge_two, verbose=verbose)

        self.fill_comparison_ions(comparison_ions, reference_spectrum, 'reference', include_charge_two=include_charge_two, verbose=verbose)

        self.normalize_comparison_ions(comparison_ions, verbose=verbose)

        #print(json.dumps(comparison_ions, indent=2, sort_keys=True))

        cosine_score = self.compute_cosine_score(comparison_ions, verbose=verbose)
        dot_product = self.compute_dot_product(comparison_ions, verbose=verbose)

        if verbose:
            self.plot_comparison_ions(comparison_ions, verbose=verbose)

        return { 'cosine_score': cosine_score, 'dot_product': dot_product }



    ####################################################################################################
    #### Annotate a spectrum using its assigned interpretation in the form of the USI
    def annotate_spectrum(self, spectrum=None, spectrum_usi=None, tolerance=None, verbose=None):

        if spectrum is None:
            eprint(f"ERROR: [annotate_spectrum] spectrum must be provided, but is None")
            return
        if spectrum_usi is None:
            eprint(f"ERROR: [annotate_spectrum] spectrum_usi must be provided, but is None")
            return
        if verbose is None:
            verbose = 0

        t0 = timeit.default_timer()
        usi_obj = UniversalSpectrumIdentifier(spectrum_usi)
        #### Need to do this as apparently the peptidoform that comes back from usi is a dict, not an object?
        peptidoforms = []
        if usi_obj.peptidoforms is not None:
            for usi_peptidoform in usi_obj.peptidoforms:
                if usi_peptidoform['peptidoform_string'] is not None and usi_peptidoform['peptidoform_string'] != '':
                    peptidoform = ProformaPeptidoform(usi_peptidoform['peptidoform_string'])
                    peptidoforms.append(peptidoform)
        t1 = timeit.default_timer()
        if verbose:
            print(f"INFO: Parsed USI in {t1-t0:.4f} seconds")
        t0 = timeit.default_timer()
        annotator = SpectrumAnnotator()
        annotator.annotate(spectrum, peptidoforms=peptidoforms, charges=usi_obj.charges, tolerance=tolerance)
        t1 = timeit.default_timer()
        if verbose:
            print(f"INFO: Annotated spectrum in {t1-t0:.4f} seconds")
        #print(reference_spectrum.show())



    ####################################################################################################
    #### Fill the comparison ions dict with either the reference or target spectrum backbone ions
    def fill_comparison_ions(self, comparison_ions, spectrum, spectrum_type, include_charge_two=True, verbose=None):

        if comparison_ions is None:
            eprint(f"ERROR: [fill_comparison_ions] comparison_ions may not be None")
            return
        if spectrum is None:
            eprint(f"ERROR: [fill_comparison_ions] spectrum may not be None")
            return
        if spectrum_type is None or spectrum_type not in [ 'target', 'reference' ]:
            eprint(f"ERROR: [fill_comparison_ions] spectrum_type must be one of (target|reference)")
            return
        if verbose is None:
            verbose = 0


        # Record the spectrum minimum mz and maximum mz
        if 'attributes' not in comparison_ions:
            comparison_ions['attributes'] = { 'minimum mz': spectrum.attributes['minimum mz'], 'maximum mz': spectrum.attributes['maximum mz'] }
        else:
            if spectrum.attributes['minimum mz'] < comparison_ions['attributes']['minimum mz']:
                comparison_ions['attributes']['minimum mz'] = spectrum.attributes['minimum mz']
            if spectrum.attributes['maximum mz'] > comparison_ions['attributes']['maximum mz']:
                comparison_ions['attributes']['maximum mz'] = spectrum.attributes['maximum mz']
        #print(json.dumps(spectrum.attributes, indent=2, sort_keys=True))
        #print(json.dumps(comparison_ions['attributes'], indent=2, sort_keys=True))

        # Loop over all peaks and record the backbone ions in the comparison_ions dict
        for i_peak in range(spectrum.attributes['number of peaks']):

            peak = spectrum.peak_list[i_peak]
            mz = peak[PL_MZ]
            intensity = peak[PL_INTENSITY]
            interpretation_string = peak[PL_INTERPRETATION_STRING]
            match = re.match(r'([by]\d+)/',interpretation_string)
            if not match and include_charge_two:
                match = re.match(r'([by]\d+\^2)/',interpretation_string)
            if match:
                ion_name = match.group(1)
                if ion_name not in comparison_ions:
                    comparison_ions[ion_name] = { 'mz': mz, 'reference_intensity': None, 'target_intensity': None }
                comparison_ions[ion_name][f"{spectrum_type}_intensity"] = intensity



    ####################################################################################################
    #### Normalize the comparison ions
    def normalize_comparison_ions(self, comparison_ions, verbose=None):

        if comparison_ions is None:
            eprint(f"ERROR: [fill_comparison_ions] comparison_ions may not be None")
            return
        if verbose is None:
            verbose = 0


        peak_maxima = { 'reference': 0.0, 'target': 0.0 }
        peak_sums = { 'reference': 0.0, 'target': 0.0 }

        # Record which peaks are outside the minimum and maximum mz
        peaks_to_delete = []
        for peak_name, intensities in comparison_ions.items():
            if peak_name == 'attributes':
                continue
            if intensities['mz'] < comparison_ions['attributes']['minimum mz']:
                peaks_to_delete.append(peak_name)
            if intensities['mz'] > comparison_ions['attributes']['maximum mz']:
                peaks_to_delete.append(peak_name)

        # Then delete them
        for peak_name in peaks_to_delete:
            del(comparison_ions[peak_name])
            if verbose:
                print(f"INFO: Deleting peak {peak_name}")

        # Always delete y1 ions since they are not diagnostic and often contaminated co-fragmented peptide ions
        if 'y1' in comparison_ions:
            del(comparison_ions['y1'])

        # Loop over all peaks and record the peak sums
        for peak_name, intensities in comparison_ions.items():
            if peak_name == 'attributes':
                continue
            for spectrum_type, current_maximum in peak_maxima.items():
                if intensities[f"{spectrum_type}_intensity"] is not None:
                    if intensities[f"{spectrum_type}_intensity"] > current_maximum:
                        peak_maxima[spectrum_type] = intensities[f"{spectrum_type}_intensity"]
                    # Only record the sums of peaks for which there are two values
                    if intensities[f"reference_intensity"] is not None and intensities[f"target_intensity"] is not None:
                        peak_sums[spectrum_type] += intensities[f"{spectrum_type}_intensity"]
        #print(f"peak_maxima={peak_maxima}")

        # Ensure the denominators are not 0
        for spectrum_type, current_maximum in peak_maxima.items():
            if current_maximum == 0.0:
                peak_maxima[spectrum_type] = 1.0

        # Loop over all peaks and divide by the sum
        overall_maximum = 0.0
        new_peak_sums = { 'reference': 0.0, 'target': 0.0 }
        for peak_name, intensities in comparison_ions.items():
            if peak_name == 'attributes':
                continue
            for spectrum_type, current_maximum in peak_sums.items():
                if current_maximum == 0:
                    current_maximum = 1.0 # Avoid division by 0
                if intensities[f"{spectrum_type}_intensity"] is not None:
                    intensities[f"{spectrum_type}_intensity"] /= current_maximum
                else:
                    intensities[f"{spectrum_type}_intensity"] = 0.0
                if intensities[f"{spectrum_type}_intensity"] > overall_maximum:
                    overall_maximum = intensities[f"{spectrum_type}_intensity"]
                new_peak_sums[spectrum_type] += intensities[f"{spectrum_type}_intensity"]
        #print(f"overall_maximum={overall_maximum}")
        #print(f"new_peak_sums={new_peak_sums}")

        # Loop over all peaks and normalize to make the tallest peak 1.0
        for peak_name, intensities in comparison_ions.items():
            if peak_name == 'attributes':
                continue
            for spectrum_type, current_maximum in peak_sums.items():
                intensities[f"{spectrum_type}_intensity_basepeak_norm"] = intensities[f"{spectrum_type}_intensity"] / overall_maximum
                divisor = new_peak_sums[spectrum_type]
                if divisor == 0:
                    divisor = 1.0
                intensities[f"{spectrum_type}_intensity"] /= divisor



    ####################################################################################################
    #### Compute a cosine score
    def compute_cosine_score(self, comparison_ions, verbose=None):

        if comparison_ions is None:
            eprint(f"ERROR: [fill_comparison_ions] comparison_ions may not be None")
            return
        if verbose is None:
            verbose = 0


        cosines_sum = 0.0
        weighted_cosines_sum = 0.0
        weights_sum = 0.0
        n_peaks = 0

        # Loop over all peaks and print some numbers
        for peak_name, intensities in comparison_ions.items():
            if peak_name == 'attributes':
                continue
            reference_intensity = intensities[f"reference_intensity_basepeak_norm"]
            target_intensity = intensities[f"target_intensity_basepeak_norm"]
            larger_intensity = reference_intensity
            if target_intensity > larger_intensity:
                larger_intensity = target_intensity
            delta = target_intensity - reference_intensity
            cosine = math.cos(delta * 3.14159/2)
            #cosine = 1 - math.fabs(delta)                              # HACK
            cosines_sum += cosine
            n_peaks += 1
            weight = larger_intensity
            if weight < 0.2:
                weight = 0.2
            weighted_cosines_sum += cosine * weight
            weights_sum += weight
            #print(f"{peak_name}\t{reference_intensity:.3f}\t{target_intensity:.3f}\t{delta:.3f}\t{cosine:.3f}\t{weight:.3f}")

        raw_cosine_score = cosines_sum / n_peaks
        weighted_cosine_score = weighted_cosines_sum / weights_sum

        if verbose:
            print(f"Raw cosine score: {raw_cosine_score:.3f}")
            print(f"Weighted cosine score: {weighted_cosine_score:.3f}")

        return weighted_cosine_score


    ####################################################################################################
    #### Compute a dot product
    def compute_dot_product(self, comparison_ions, verbose=None):

        if comparison_ions is None:
            eprint(f"ERROR: [fill_comparison_ions] comparison_ions may not be None")
            return
        if verbose is None:
            verbose = 0

        dot_product_sum = 0.0

        # Loop over all peaks and print some numbers
        for peak_name, intensities in comparison_ions.items():
            if peak_name == 'attributes':
                continue
            reference_intensity = intensities[f"reference_intensity"]
            target_intensity = intensities[f"target_intensity"]
            dot_product = math.sqrt(reference_intensity * target_intensity)
            dot_product_sum += dot_product
            #print(f"{peak_name}\t{reference_intensity:.3f}\t{target_intensity:.3f}\t{dot_product:.3f}\t{dot_product_sum:.3f}")

        if verbose:
            print(f"Dot product: {dot_product_sum:.3f}")

        return dot_product_sum


    ####################################################################################################
    #### Plot the comparison ions
    def plot_comparison_ions(self, comparison_ions, verbose=None):

        if comparison_ions is None:
            eprint(f"ERROR: [fill_comparison_ions] comparison_ions may not be None")
            return
        if verbose is None:
            verbose = 0


        spectrum_types = { 'reference': 'b', 'target': 'r' }

        # Loop over all peaks and plot them
        for peak_name, attributes in comparison_ions.items():
            if peak_name == 'attributes':
                continue
            offset = 0
            for spectrum_type, color in spectrum_types.items():
                mz = attributes['mz']
                intensity = attributes[f"{spectrum_type}_intensity"]
                if intensity is not None:
                    plt.plot([mz+offset,mz+offset], [0, intensity], c=color)
                offset += 10

        plt.show()


#for value in [ -0.2, 0.001, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0 ]:
#    print(f"{value:.3f}\t{math.cos(value*3.14159/2)}\t{1-math.fabs(value)}\t{1 / (1 + math.exp(-value)):.3f}")


####################################################################################################
#### For command-line usage
def main():

    argparser = argparse.ArgumentParser(description='Class to compare two spectra, computing various similarity scores')
    argparser.add_argument('--verbose', action='count', help='If set, print more information about ongoing processing' )
    argparser.add_argument('--target_spectrum_usi', action='store', default=None, type=str, help='Target spectrum USI')
    argparser.add_argument('--reference_spectrum_usi', action='store', default=None, type=str, help='Reference spectrum USI')
    argparser.add_argument('--tolerance', action='store', default=None, type=str, help='Tolerance for annotation and comparison in ppm')
    argparser.add_argument('--test', action='store', type=str, help='Set to a test tag to run, e.g. 1, 2, 3, or 4')
    params = argparser.parse_args()

    # Set verbose mode
    verbose = params.verbose
    if verbose is None:
        verbose = 0

    # If --test is supplied, then set two example USIs
    usi = None
    if params.test is not None and params.test != '':
        if params.test == '1':
            params.target_spectrum_usi = 'mzspec:PXD014017:20180821_QE_HFX_LC2_SA_JMI_HLAIp_CRC-01_IFN2_R02:scan:51704:RLTDQSRWSW/2'
            params.reference_spectrum_usi = 'mzspec:PXD990004:PL57-SyntheticPeptides-hcd27_OT_DDA:scan:11533:RLTDQSRWSW/2'
            params.reference_spectrum_usi = 'mzspec:MS2PIP:HCD:scan:1:RLTDQSRWSW/2'
        elif params.test == '2':
            params.target_spectrum_usi = 'mzspec:PXD000394:20120726_EXQ1_MiBa_SA_SupB15-RT_mHLA-1:scan:34218:VVDASFFLK/1'
            params.reference_spectrum_usi = 'mzspec:PXD990004:PL57-SyntheticPeptides-hcd25_OT_DDA_2:scan:14567:VVDASFFLK/1'
            params.reference_spectrum_usi = 'mzspec:MS2PIP:HCD:scan:1:VVDASFFLK/1'
        elif params.test == '3':
            params.target_spectrum_usi = 'mzspec:PXD020389:20171031_QE5_nLC3_AKP_UBIsite_SY5Y_CBLsKD_L-H_E1_17F_14:scan:5621:PLHGALQSASR/2'
            params.reference_spectrum_usi = 'mzspec:PXD990004:PL57-SyntheticPeptides-hcd28_OT_DDA:scan:4753:PLHGALQSASR/2'
            params.reference_spectrum_usi = 'mzspec:MS2PIP:HCD:scan:1:PLHGALQSASR/2'
        elif params.test == '4':
            params.target_spectrum_usi = 'mzspec:PXD020389:20171031_QE5_nLC3_AKP_UBIsite_SY5Y_CBLsKD_L-H_E1_17F_14:scan:5621:PLHGALQSASR/2'
            params.reference_spectrum_usi = 'mzspec:PXD990004:PL57-SyntheticPeptides-hcd27_OT_DDA:scan:11533:PLHGALQSASR/2' # wrong spectrum for this peptide, should be a terrible match
        elif params.test == '5':
            params.target_spectrum_usi = 'mzspec:PXD000612:20120224_EXQ5_KiSh_SA_LabelFree_HeLa_Phospho_EGF_rep1_Fr4:scan:10072:M[Oxidation]VLNQDDHDDNDNEDDVNTAEK/3'
            params.reference_spectrum_usi = 'mzspec:MS2PIP:HCD:scan:10072:M[Oxidation]VLNQDDHDDNDNEDDVNTAEK/3'
        if verbose:
            eprint(f"INFO: Using two test USIs for peptidoform ion RLTDQSRWSW/2")

    # Verify that we have both spectra
    if params.target_spectrum_usi is None or params.target_spectrum_usi == '':
        eprint(f"ERROR: --target_spectrum_usi must be specified")
        return
    if params.reference_spectrum_usi is None or params.reference_spectrum_usi == '':
        eprint(f"ERROR: --reference_spectrum_usi must be specified")
        return

    if params.tolerance is None:
        params.tolerance = 10.0
        eprint(f"INFO: Using default tolerance of {params.tolerance} ppm")

    spectrum_comparator = SpectrumComparator()
    comparison_scores = spectrum_comparator.compare_usis(reference_spectrum_usi=params.reference_spectrum_usi, target_spectrum_usi=params.target_spectrum_usi, tolerance=params.tolerance, verbose=verbose)

    print(f"Comparison scores: {comparison_scores}")


#### For command line usage
if __name__ == "__main__": main()
