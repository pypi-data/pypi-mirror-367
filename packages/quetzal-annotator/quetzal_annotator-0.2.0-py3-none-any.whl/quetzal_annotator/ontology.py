#!/usr/bin/env python3

import sys
import logging
import re
import timeit
import json
import argparse

def eprint(*args, **kwargs): print(*args, file=sys.stderr, **kwargs)

from quetzal_annotator.ontology_term import OntologyTerm


#############################################################################
#### Ontology class
class Ontology(object):


    #########################################################################
    #### Constructor
    def __init__(self, filename=None, verbose=0):

        self.filename = filename
        self.verbose = verbose

        self.is_valid = False
        self.n_terms = 0
        self.primary_prefix = None
        self.prefixes = {}
        self.header_line_list = []
        self.other_line_list = []
        self.term_list = []
        self.terms = {}

        self.names = {}
        self.uc_names = {}
        self.mass_mod_names = {}
        self.mass_mod_names_extended = {}
        self.uc_mass_mod_names = {}

        self.n_errors = 0
        self.error_code = None
        self.error_message = None

        self.uc_search_string = None

        #### If we have been given a filename on construction, read it right away
        if filename:
            self.read()
        

    #########################################################################
    #### Write all ontology information out as a json representation
    def write_json(self, filename, verbose=0):
        with open(filename, 'w') as outfile:
            container = {
                'is_valid': self.is_valid,
                'n_terms': self.n_terms,
                'primary_prefix': self.primary_prefix,
                'prefixes': self.prefixes,
                'header_line_list': self.header_line_list,
                'other_line_list': self.other_line_list,
                'term_list': self.term_list,
                #'terms': self.terms,
                'names': self.names,
                'uc_names': self.uc_names,
                'mass_mod_names': self.mass_mod_names,
                'mass_mod_names_extended': self.mass_mod_names_extended,
                'uc_mass_mod_names': self.uc_mass_mod_names,
                'n_errors': self.n_errors,
                'error_code': self.error_code,
                'error_message': self.error_message,
                'uc_search_string': self.uc_search_string
            }

            # The terms are all OntologyTerm objects, so need to serialize them to a dict for JSON output
            serialized_terms = {}
            for key, obj in self.terms.items():
                serialized_obj = obj.__dict__
                serialized_obj['line_list'] = []
                serialized_terms[key] = serialized_obj
            container['terms'] = serialized_terms

            json.dump(container, outfile, indent=2)


    #########################################################################
    #### Read all ontology information from the json representation
    def read_json(self, filename, verbose=0):
        with open(filename) as infile:
            container = json.load(infile)
            self.is_valid = container['is_valid']
            self.n_terms = container['n_terms']
            self.primary_prefix = container['primary_prefix']
            self.prefixes = container['prefixes']
            self.header_line_list = container['header_line_list']
            self.other_line_list = container['other_line_list']
            self.term_list = container['term_list']
            #self.terms = container['terms']
            self.names = container['names']
            self.uc_names = container['uc_names']
            self.mass_mod_names = container['mass_mod_names']
            self.mass_mod_names_extended = container['mass_mod_names_extended']
            self.uc_mass_mod_names = container['uc_mass_mod_names']
            self.n_errors = container['n_errors']
            self.error_code = container['error_code']
            self.error_message = container['error_message']
            self.uc_search_string = container['uc_search_string']

            self.terms = {}
            for key, term_dict in container['terms'].items():
                term = OntologyTerm()
                term.line_list = term_dict['line_list']
                term.verbose = term_dict['verbose']

                term.is_valid = term_dict['is_valid']
                term.prefix = term_dict['prefix']
                term.identifier = term_dict['identifier']
                term.curie = term_dict['curie']
                term.name = term_dict['name']
                term.value_type = term_dict['value_type']
                term.definition = term_dict['definition']
                term.origin = term_dict['origin']
                term.unparsable_line_list = term_dict['unparsable_line_list']
                term.origin = term_dict['origin']
                term.xref_list = term_dict['xref_list']
                term.relationship_list = term_dict['relationship_list']
                term.parents = term_dict['parents']
                term.children = term_dict['children']
                term.synonyms = term_dict['synonyms']
                term.xrefs = term_dict['xrefs']
                term.has_units = term_dict['has_units']
                term.has_order = term_dict['has_order']
                term.has_domain = term_dict['has_domain']
                term.has_regexp = term_dict['has_regexp']
                term.is_obsolete = term_dict['is_obsolete']
                term.namespaces = term_dict['namespaces']
                term.subsets = term_dict['subsets']

                term.monoisotopic_mass = term_dict['monoisotopic_mass']
                term.average_mass = term_dict['average_mass']
                term.sites = term_dict['sites']
                term.extended_name = term_dict['extended_name']

                term.n_errors = term_dict['n_errors']
                term.error_code = term_dict['error_code']
                term.error_message = term_dict['error_message']
                self.terms[key] = term



    #########################################################################
    #### parse the file
    def read(self, filename=None, verbose=0):
        # verboseprint = print if verbose>0 else lambda *a, **k: None
        if verbose > 0:
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)

        #### Determine the filename to read
        if filename is not None:
            self.filename = filename
        filename = self.filename

        #### If the filename ends in json, then flip over to the json reader
        if filename.endswith('.json'):
            self.read_json(filename=filename)
            return

        #### Set up some beginning statement
        state = 'header'
        terms_list = []
        terms = {}
        current_term = []

        logging.info("Reading file '%s'", filename)
        with open(filename, encoding="latin-1", errors="replace") as infile:
            for line in infile:
                line = line.rstrip()

                #### Process the header
                if state == 'header':
                    match = re.search(r"^\s*\[Term\]\s*$",line)
                    if match:
                        state = 'term'
                    else:
                        self.header_line_list.append(line)

                #### Process the other elements in the file
                if state == 'other':
                    match = re.search(r"^\s*\[Term\]\s*$",line)
                    if match:
                        state = 'term'
                    else:
                        self.other_line_list.append(line)

                #### Process the term section
                if state == 'term':

                    #### Skip an empty line
                    match = re.search(r"^\s*$",line)
                    if match:
                        continue

                    #### If this is a new element
                    match = re.search(r"^\s*\[",line)
                    if match:

                        #### If this is a new [Term]
                        match = re.search(r"^\s*\[Term\]\s*$",line)
                        if match:

                            #### If there is currently something in the buffer, process it
                            #### WARNING: If any changes are made here, you also need to update after the loop for the processing of the last term
                            if len(current_term) > 0:
                                #### Store this term
                                term = OntologyTerm(line_list=current_term, verbose=verbose)
                                if term.is_obsolete is False:
                                    self.term_list.append(term.curie)
                                    if term.curie in self.terms:
                                        self.set_error("Duplicate term!")
                                    else:
                                        self.terms[term.curie] = term
                                        if term.prefix not in self.prefixes:
                                            self.prefixes[term.prefix] = 0
                                        self.prefixes[term.prefix] += 1

                                #### Clear current term data and update counters
                                current_term = []
                                self.n_terms += 1

                            #### Append the current line to the working term buffer
                            current_term.append(line)

                        #### Otherwise this is the start of some non-Term thing
                        else:
                            state = 'other'
                            self.other_line_list.append(line)

                    #### Otherwise, just append the current line to the working term buffer
                    else:
                        current_term.append(line)

        #### Process a last term that still may be in the buffer
        if len(current_term) > 0:
            #### Store this term
            term = OntologyTerm(line_list=current_term, verbose=verbose)
            if term.is_obsolete is False:
                self.term_list.append(term.curie)
                if term.curie in self.terms:
                    self.set_error("Duplicate term!")
                else:
                    self.terms[term.curie] = term
                    if term.prefix not in self.prefixes:
                        self.prefixes[term.prefix] = 0
                    self.prefixes[term.prefix] += 1

            current_term = []
            self.n_terms += 1

        #### Now map the parentage structure into children
        self.map_children(verbose=verbose)

        #### And create the map of names
        self.create_name_map(verbose=verbose)

        #### If this is Unimod, create a special name_map that includes mass deltas
        if 'UNIMOD' in self.prefixes:
            self.create_mass_mod_map(verbose=verbose)

        #### Set the is_valid state
        if self.n_errors == 0:
           self.is_valid = True

        else:
            self.is_valid = False
            logging.critical(f"Number of errors in file %s: %s", self.filename, self.n_error)
 
 
    #########################################################################
    #### Map all the parent relationships to child relationships for the parent
    def map_children(self, verbose=0):
        # verboseprint = print if verbose>0 else lambda *a, **k: None
        if verbose > 0:
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)

        logging.info("Mapping parents to children")
        for curie in self.term_list:
            term = self.terms[curie]
            parents = term.parents
            for parent in parents:
                parent_curie = parent['curie']
                type = parent['type']
                new_type = '??'
                if type == 'is_a': new_type = 'has_subclass'
                if type == 'part_of': new_type = 'has_part'
                if parent_curie in self.terms:
                    self.terms[parent_curie].children.append( { 'type': new_type, 'curie': curie } )
                else:
                    if parent_curie != 'UO:0000000':
                        logging.error(
                            "'%s' has parent '%s', but this curie is not found in this ontology",
                            curie, parent_curie
                        )


    #########################################################################
    #### Create a dict of all the names and synonyms
    def create_name_map(self, verbose=0):
        # verboseprint = print if verbose>0 else lambda *a, **k: None
        if verbose > 0:
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)

        logging.info("Creating a dict of all names and synonyms")
        for curie in self.term_list:
            term = self.terms[curie]
            names = [ term.name ]
            for synonym in term.synonyms:
                names.append(synonym['term'])
            for name in names:
                if name is None:
                    #print(f"WARNING: Term {curie} has no name!")
                    name = curie
                if name in self.names:
                    self.names[name].append(curie)
                else:
                    self.names[name] = [ curie ]
                uc_name = name.upper()
                if uc_name in self.uc_names:
                    #self.uc_names[uc_name].append(curie)
                    self.uc_names[uc_name][curie] = 1
                else:
                    #self.uc_names[uc_name] = [ curie ]
                    self.uc_names[uc_name] = { curie: 1 }


    #########################################################################
    #### Create a dict of all the names and synonyms
    def create_mass_mod_map(self, verbose=0):

        logging.info("Creating a mass mod map")
        for curie in self.term_list:
            term = self.terms[curie]
            name = term.name
            if name is None:
                print(f"WARNING: Term {curie} has no name!")
                name = curie

            #### Get a clean monoisotopic_mass
            monoisotopic_mass = term.monoisotopic_mass
            if monoisotopic_mass is None:
                monoisotopic_mass = 0

            #### Set a special string to make sure there is always a sign displayed
            sign_str = ''
            if monoisotopic_mass >= 0:
                sign_str = '+'

            sites = term.sites
            if sites is None:
                sites = [ '? ']

            #### Loop over all possible sites and make names
            for site in sites:
                extended_name = f"{name} ({site}{sign_str}{monoisotopic_mass})"
                extended_curie = f"{curie}-{site}"
                if extended_name in self.mass_mod_names:
                    self.mass_mod_names[extended_name].append(extended_curie)
                else:
                    self.mass_mod_names[extended_name] = [ extended_curie ]
                    self.mass_mod_names_extended[extended_curie] = extended_name
                term.extended_name = f"{name} ({sign_str}{monoisotopic_mass})"

                #### Also save the upper-case versions
                uc_name = extended_name.upper()
                if uc_name in self.uc_mass_mod_names:
                    self.uc_mass_mod_names[uc_name].append(extended_curie)
                else:
                    self.uc_mass_mod_names[uc_name] = [ extended_curie ]

    #########################################################################
    #### Get a list of all children of a term
    def get_children(self, parent_curie, return_type='ucdict'):

        if parent_curie not in self.terms:
            return([])

        children_curies = {}

        parent_term = self.terms[parent_curie]
        children = parent_term.children

        while len(children) > 0:
            new_children = []
            for child in children:
                child_curie = child['curie']
                children_curies[child_curie] = 1
                child_term = self.terms[child_curie]
                if len(child_term.children) > 0:
                    new_children.extend(child_term.children)
            children = []
            children.extend(new_children)

        result_list = []
        results = {}
        for child in children_curies:
            if return_type == 'ucdict':
                results[self.terms[child].name.upper()] = [child]
            if return_type == 'uclist':
                result_list.append(self.terms[child].name.upper())
            if return_type == 'term_tuples':
                result_list.append({ 'curie': child, 'name': self.terms[child].name })

        if return_type == 'ucdict':
            return(results)
        if return_type == 'uclist':
            return(result_list)
        if return_type == 'term_tuples':
            return(sorted(result_list,key=lambda x: x['name'].lower()))



    #########################################################################
    #### Fuzzy search for a string
    def fuzzy_search(self, search_string, max_hits=15, children_of=None):

        match_term_list = []
        match_curies = {}

        logging.info("Executing fuzzy search for '%s'", search_string)
        search_space = self.uc_names
        if children_of is not None:
            search_space = self.get_children(parent_curie=children_of, return_type='ucdict')

        self.uc_search_string = search_string.upper()
        match_list = filter(self.filter_starts_with,search_space)
        for match in match_list:
            curies = search_space[match]
            curie = curies[0]
            if curie in match_curies: continue
            match_curies[curie] = 1
            #print("--",curie)
            term = { 'curie': curie, 'name': self.terms[curie].name, 'sort': 1 }
            match_term_list.append(term)

        count = len(match_term_list)

        if count < max_hits:
            matches = filter(self.filter_contains,search_space)
            for match in matches:
                curies = search_space[match]
                curie = curies[0]
                if curie in match_curies: continue
                match_curies[curie] = 1
                #print("==",curie)
                term = { 'curie': curie, 'name': self.terms[curie].name, 'sort': 2 }
                match_term_list.append(term)

        sorted_match_term_list = sorted(match_term_list,key=sort_by_relevance)
        if len(sorted_match_term_list) > max_hits:
            del sorted_match_term_list[max_hits:]

        for match in sorted_match_term_list:
            del match['sort']

        return(sorted_match_term_list)


    #########################################################################
    #### Fuzzy search for a string
    def fuzzy_mass_mod_search(self, search_string, max_hits=25, children_of=None):

        match_term_list = []
        match_curies = {}

        logging.info("Executing fuzzy search for '%s'", search_string)
        search_space = self.uc_mass_mod_names
        if children_of is not None:
            search_space = self.get_children(parent_curie=children_of, return_type='ucdict')

        #### Convert the search string to upper case (for case-insensitive search)
        self.uc_search_string = search_string.upper()
        #### Replace any + symbols with \+ for the regexp to work
        self.uc_search_string = re.sub(r'\+','\+',self.uc_search_string)
        #### Replace any . symbols with \. for the regexp to work
        self.uc_search_string = re.sub(r'\.','\.',self.uc_search_string)

        match_list = filter(self.filter_starts_with,search_space)
        for match in match_list:
            curies = search_space[match]
            curie = curies[0]
            if curie in match_curies: continue
            match_curies[curie] = 1
            trimmed_curie = re.sub(r'-.+$','',curie)
            term = { 'curie': trimmed_curie, 'name': self.mass_mod_names_extended[curie], 'sort': 1 }
            match_term_list.append(term)

        count = len(match_term_list)

        if count < max_hits:
            matches = filter(self.filter_contains,search_space)
            for match in matches:
                curies = search_space[match]
                curie = curies[0]
                if curie in match_curies: continue
                match_curies[curie] = 1
                trimmed_curie = re.sub(r'-.+$','',curie)
                term = { 'curie': trimmed_curie, 'name': self.mass_mod_names_extended[curie], 'sort': 2 }
                match_term_list.append(term)

        sorted_match_term_list = sorted(match_term_list,key=sort_by_relevance)
        if len(sorted_match_term_list) > max_hits:
            del sorted_match_term_list[max_hits:]

        for match in sorted_match_term_list:
            del match['sort']

        return(sorted_match_term_list)


    #########################################################################
    # Set the ontology to the error state
    def set_error(self, error_code, error_message):
        self.error_code = error_code
        self.error_message = error_message
        self.n_errors += 1
        logging.error("(%s): %s", error_code, error_message)


    #########################################################################
    # Print out some information about the ontology
    def show(self):
        print(f"filename: {self.filename}")
        print(f"is_valid: {self.is_valid}")
        print(f"Number of errors: {self.n_errors}")
        print(f"Number of terms: {self.n_terms}")
        print(f"Number of header lines: {len(self.header_line_list)}")
        print(f"prefixes: {self.prefixes}")

        print(f"Number of other lines: {len(self.other_line_list)}")
        if len(self.other_line_list) > 0:
            i_other_line = 0
            for line in self.other_line_list:
                print("  >"+line)
                i_other_line += 1
                if i_other_line > 15: break
            print("  >...")


    #########################################################################
    #### filtering routines
    def filter_starts_with(self,x):
        match = re.match(self.uc_search_string,x)
        if match: return(True)
        return(False)
    def filter_contains(self,x):
        match = re.search(self.uc_search_string,x)
        if match: return(True)
        return(False)



#########################################################################
#### sorting routines
def sort_by_relevance(x):
    value = x['sort'] * 1000 + len(x['name'])
    return(value)



#########################################################################
#### A very simple example of using this class
def psims_example(filename='psi-ms.json'):
    ontology = Ontology(filename=filename,verbose=1)
    ontology.show()
    print("============================")
    term = ontology.terms["MS:1002286"]
    term.show()
    print("============================")
    name = 'QIT'
    print(f"Searching for '{name}'")
    if name in ontology.names:
        curies = ontology.names[name]
        for curie in curies:
            term = ontology.terms[curie]
            term.show()
    print("============================")
    name = 'bit'
    result_list = ontology.fuzzy_search(search_string=name)
    for item in result_list:
        print(item)
    print("============================")
    name = 'bit'
    result_list = ontology.fuzzy_search(search_string=name, children_of="MS:1000031")
    for item in result_list:
        print(item)


#### A simple example reading and accessing the UNIMOD ontology
def unimod_example(filename='unimod.json'):
    ontology = Ontology(filename=filename,verbose=1)
    ontology.show()
    print("============================")
    term = ontology.terms["UNIMOD:7"]
    term.show()
    print("============================")
    name = 'S+79'
    result_list = ontology.fuzzy_mass_mod_search(search_string=name)
    for item in result_list:
        print(item)
    print("============================")
    return ontology



####################################################################################################
#### For command-line usage
def main():

    argparser = argparse.ArgumentParser(description='Class representing an ontology or controlled vocabulary')
    argparser.add_argument('--verbose', action='count', help='If set, print more information about ongoing processing' )
    argparser.add_argument('--convert_to_json', action='count', help='If set, convert the input file to a JSON file')
    argparser.add_argument('--input_filename', action='store', default=None, help='Filename of the ontology')
    argparser.add_argument('--identifier', action='store', default=None, help='Identifier of the term to show')
    argparser.add_argument('--unimod_example', action='count', help='If set, run a few example calls for Unimod terms' )
    argparser.add_argument('--psims_example', action='count', help='If set, run a few example calls for PSI-MS terms' )
    params = argparser.parse_args()

    # Set verbose mode
    verbose = params.verbose
    if verbose is None:
        verbose = 0

    if params.unimod_example is not None:
        eprint('Running Unimod example')
        t0 = timeit.default_timer()
        ontology = unimod_example()
        t1 = timeit.default_timer()
        print('INFO: Elapsed time: ' + str(t1-t0))
        return

    if params.psims_example is not None:
        eprint('Running PSI-MS example')
        t0 = timeit.default_timer()
        ontology = psims_example()
        t1 = timeit.default_timer()
        print('INFO: Elapsed time: ' + str(t1-t0))
        return

    input_filename = 'unimod.json'
    if params.input_filename is not None:
        input_filename = params.input_filename

    identifier = None
    if params.identifier is not None:
        identifier = params.identifier

    if input_filename is not None and identifier is not None:
        eprint(f"INFO: Fetching {identifier} from {input_filename}")
        t0 = timeit.default_timer()
        ontology = Ontology(filename=input_filename, verbose=verbose)
        if identifier in ontology.terms:
            term = ontology.terms[identifier]
            term.show()
            t1 = timeit.default_timer()
            print('INFO: Elapsed time: ' + str(t1-t0))
        else:
            eprint(f"INFO: Term {identifier} not found in ontoloy {input_filename}")
        return

    if input_filename is not None and params.convert_to_json is not None:
        eprint(f"INFO: Loading ontology from {input_filename}")
        t0 = timeit.default_timer()
        ontology = Ontology(filename=input_filename, verbose=verbose)
        output_filename = input_filename.replace('obo', 'json')
        if output_filename == input_filename:
            eprint(f"ERROR: Unable to translate '.obo' to '.json' in filename {input_filename}")
            return
        eprint(f"INFO: Loading ontology from {input_filename}")
        t1 = timeit.default_timer()
        print('INFO: Elapsed time: ' + str(t1-t0))
        eprint(f"INFO: Writing ontology to {output_filename}")
        ontology.write_json(output_filename)
        t2 = timeit.default_timer()
        print('INFO: Elapsed time: ' + str(t2-t1))
        return

    eprint(f"INFO: Insufficient parameters to know what to do. Use --help for more information")



if __name__ == "__main__": main()
