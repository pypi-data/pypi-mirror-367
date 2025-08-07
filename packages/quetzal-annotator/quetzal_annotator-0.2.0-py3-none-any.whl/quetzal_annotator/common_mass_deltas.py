#!/usr/bin/env python3

import sys
import argparse
def eprint(*args, **kwargs): print(*args, file=sys.stderr, **kwargs)

from quetzal_annotator.proforma_peptidoform import ProformaPeptidoform


####################################################################################################
#### CommonMassDeltas class
class CommonMassDeltas:

    #### Constructor
    def __init__(self, verbose=1):
        """
        __init__ - CommonMassDeltas constructor

        Parameters
        ----------
        attribute_list: list
            A list of attribute [key, value (, group)] sets to initialize to.
        """

        self.verbose = verbose

        self.common_mass_mods = self.define_mass_mods()

        self.common_residues = self.define_common_residues()

        self.deltas = self.compute_common_mass_deltas()


    ####################################################################################################
    #### Define a set of common mass mods that we'll consider
    def define_mass_mods(self):

        return [
            'C[Carbamidomethyl]',
            'M[Oxidation]',
            'N[Deamidated]',
            'Q[Deamidated]',
            'S[Phospho]',
            'T[Phospho]',
            'Y[Phospho]',
            'K[TMT6plex]',
            'K[TMTpro]',
            'S[TMTpro]',
            'T[TMTpro]',
            'R[TMTpro]',
            'K[iTRAQ8plex]',
            'K[GG]',
            'K[Acetyl]',
            'K[Dimethyl]',
            'C[Propionamide]',
            'W[Oxidation]',
            'W[Dioxidation]',
            'W[Trioxidation]',
            'H[Oxidation]',
            'C[Cysteinyl]',
            'H[Carbamidomethyl]',
            'K[Carbamidomethyl]',
            'W[Trp->Kynurenin]',
            'K[Carbamyl]',
            'C[Dioxidation]',
            'C[Trioxidation]',
            'S[Dehydrated]',
            'T[Dehydrated]',
            'C[Dehydroalanine]',
            'D[Cation:Al[III]]',
            'E[Cation:Al[III]]',
            'D[Cation:Fe[III]]',
            'E[Cation:Fe[III]]',
            'D[Cation:Na]',
            'E[Cation:Na]',
            'D[Cation:Ca[II]]',
            'E[Cation:Ca[II]]',
            'D[Cation:K]',
            'E[Cation:K]',
        ]


    ####################################################################################################
    #### Define a set of common mass mods that we'll consider
    def define_common_residues(self):

        aa_masses = {
            'G': 57.021463735,
            'A': 71.037113805,
            'S': 87.032028435,
            'P': 97.052763875,
            'V': 99.068413945,
            'T': 101.047678505,
            'C': 103.009184505,
            'L': 113.084064015,
            'I': 113.084064015,
            'N': 114.042927470,
            'D': 115.026943065,
            'Q': 128.058577540,
            'K': 128.094963050,
            'E': 129.042593135,
            'M': 131.040484645,
            'H': 137.058911875,
            'F': 147.068413945,
            'U': 150.953633405,  # selenocysteine
            'R': 156.101111050,
            'Y': 163.063328575,
            'W': 186.079312980,
        }
 
        all_mass_mods_string = ''.join(self.common_mass_mods)
        peptidoform = ProformaPeptidoform(all_mass_mods_string)

        all_residues = aa_masses.copy()
        for residue in peptidoform.residues:
            if 'base_residue' in residue:
                all_residues[residue['residue_string']] = aa_masses[residue['base_residue']] + residue['delta_mass']

        return all_residues


    ####################################################################################################
    #### Comptue a set of common mass deltas between 0 and 400
    def compute_common_mass_deltas(self):

        common_mass_deltas = []
        for residue1, mass1 in self.common_residues.items():
            common_mass_deltas.append( [ mass1, residue1 ] )
            for residue2, mass2 in self.common_residues.items():
                residues = residue1 + residue2
                mass = mass1 + mass2
                if mass < 400:
                    common_mass_deltas.append( [ mass, residues ] )
                for residue3, mass3 in self.common_residues.items():
                    residues = residue1 + residue2 + residue3
                    mass = mass1 + mass2 + mass3
                    if mass < 400:
                        common_mass_deltas.append( [ mass, residues ] )

        common_mass_deltas.sort(key=lambda x: x[0])
        return common_mass_deltas


####################################################################################################
#### For command-line usage
def main():

    argparser = argparse.ArgumentParser(description='Utility to fetch spectra via USIs')
    argparser.add_argument('--verbose', action='count', help='If set, print more information about ongoing processing' )
    argparser.add_argument('--test', action='count', help='If set, just use an example USI to test')
    argparser.add_argument('--write', action='count', help='If set, write out the output file common_mass_deltas.tsv')
    params = argparser.parse_args()

    # Set verbose mode
    verbose = params.verbose
    if verbose is None:
        verbose = 1

    common_mass_deltas = CommonMassDeltas()
    #print(json.dumps(common_mass_deltas.common_residues, indent=2))

    #### If --test is specified, print out a few lines and end
    if params.test is not None:
        i = 0
        for line in common_mass_deltas.deltas:
            print(f"{line[0]:8.4f}\t{line[1]}")
            i += 1
            if i > 50:
                break
        return

    #### If --write is specified, write everything to a file
    if params.write is not None:
        with open('common_mass_deltas.tsv', 'w') as outfile:
            for line in common_mass_deltas.deltas:
                print(f"{line[0]:8.4f}\t{line[1]}", file=outfile)
        return

    print("ERROR: Nothing to do. Supply --help, --test, or --write")

#### For command line usage
if __name__ == "__main__": main()
