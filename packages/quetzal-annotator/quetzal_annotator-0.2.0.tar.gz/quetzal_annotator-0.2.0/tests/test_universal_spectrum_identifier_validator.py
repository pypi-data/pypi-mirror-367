import pytest
import sys
import json

from quetzal_annotator import UniversalSpectrumIdentifierValidator


def test_init_without_usi_list():
    validator = UniversalSpectrumIdentifierValidator()
    assert validator.usi_list is None
    assert validator.response['error_code'] == 'OK'


def test_init_with_usi_list():
    usi_list = [ "mzspec:PXD002437:00261_A06_P001564_B00E_A00_R1:scan:10951" ]
    validator = UniversalSpectrumIdentifierValidator(usi_list=usi_list)
    assert validator.usi_list == usi_list
    assert validator.response['error_code'] == 'OK'
    assert "mzspec:PXD002437:00261_A06_P001564_B00E_A00_R1:scan:10951" in validator.response['validation_results']


def test_set_error():
    validator = UniversalSpectrumIdentifierValidator()
    validator.set_error("TestError", "This is a test error")
    assert validator.error_code == "TestError"
    assert validator.error_message == "This is a test error"
    assert validator.response['error_code'] == "TestError"
    assert validator.response['error_message'] == "This is a test error"


def test_valid_usi_list():
    validator = UniversalSpectrumIdentifierValidator()
    usi_list = validator.get_example_valid_usi_list()
    assert len(usi_list) > 10
    for usi in usi_list:
        validator.validate_usi_list( [usi] )
        assert validator.response['error_code'] == 'OK'
        assert validator.response['validation_results'][usi]['is_valid'] == True


def test_invalid_usi_list():
    validator = UniversalSpectrumIdentifierValidator()
    usi_list = validator.get_example_invalid_usi_list()
    assert len(usi_list) > 7
    for usi in usi_list:
        validator.validate_usi_list( [usi] )
        print(json.dumps(validator.response, indent=2))
        assert validator.response['error_code'] == 'OK'
        assert validator.response['validation_results'][usi]['is_valid'] == False


def test_detailed_validation_information():
    usi = "mzspec:PXD000000:a:scan:1:{Hex|INFO:completely labile}[iTRAQ4plex]-EM[Oxidation]EVNESPEK[UNIMOD:214]-[Methyl]/2"
    validator = UniversalSpectrumIdentifierValidator( [usi] )
    assert validator.response['error_code'] == 'OK'
    assert validator.response['validation_results'][usi]['is_valid'] == True
    assert validator.response['validation_results'][usi]['charge'] == 2
    assert len(validator.response['validation_results'][usi]['charges']) == 1
    assert validator.response['validation_results'][usi]['ms_run_name'] == 'a'
    assert len(validator.response['validation_results'][usi]['peptidoform']['residue_modifications']) == 2
    assert len(validator.response['validation_results'][usi]['peptidoform']['residues']) == 12
    assert len(validator.response['validation_results'][usi]['peptidoform']['terminal_modifications']) == 2
    assert len(validator.response['validation_results'][usi]['peptidoform']['unlocalized_mass_modifications']) == 1
    assert validator.response['validation_results'][usi]['usi'] == usi
