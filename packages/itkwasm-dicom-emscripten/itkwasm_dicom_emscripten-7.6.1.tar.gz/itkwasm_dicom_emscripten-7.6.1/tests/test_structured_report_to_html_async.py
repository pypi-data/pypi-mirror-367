import sys

if sys.version_info < (3,10):
    pytest.skip("Skipping pyodide tests on older Python", allow_module_level=True)

from pytest_pyodide import run_in_pyodide
from pytest_pyodide.decorator import copy_files_to_pyodide
from .fixtures import input_file_list

file_list = input_file_list()

@copy_files_to_pyodide(file_list=file_list,install_wheels=True)
@run_in_pyodide
async def test_structured_report_to_html(selenium):
    from pathlib import Path

    from itkwasm_dicom_emscripten import structured_report_to_html_async

    test_file_path = '88.33-comprehensive-SR.dcm'
    assert Path(test_file_path).exists()

    output_text = await structured_report_to_html_async(test_file_path)
    assert output_text.find('Comprehensive SR Document') != -1
    assert output_text.find('Breast Diagnosis 010001 (female, #BreastDx-01-0001)') != -1
    assert output_text.find('PixelMed (XSLT from di3data csv extract)') != -1

    output_text = await structured_report_to_html_async(test_file_path, no_document_header=True)
    assert output_text.find('Breast Diagnosis 010001 (female, #BreastDx-01-0001)') == -1
    assert output_text.find('PixelMed (XSLT from di3data csv extract)') == -1

    output_text = await structured_report_to_html_async(test_file_path, render_all_codes=True)
    assert output_text.find('Overall Assessment (111413, DCM)') != -1

@copy_files_to_pyodide(file_list=file_list,install_wheels=True)
@run_in_pyodide
async def test_read_radiation_dose_sr(selenium):
    from pathlib import Path

    from itkwasm_dicom_emscripten import structured_report_to_html_async

    test_file_path = '88.67-radiation-dose-SR.dcm'
    assert Path(test_file_path).exists()

    output_text = await structured_report_to_html_async(test_file_path)
    assert output_text.find('<title>X-Ray Radiation Dose SR Document</title>') != -1
    assert output_text.find('<h2>CT Accumulated Dose Data</h2>') != -1

@copy_files_to_pyodide(file_list=file_list,install_wheels=True)
@run_in_pyodide
async def test_read_key_object_selection_sr(selenium):
    from pathlib import Path

    from itkwasm_dicom_emscripten import structured_report_to_html_async

    test_file_path = '88.59-KeyObjectSelection-SR.dcm'
    assert Path(test_file_path).exists()

    url_prefix = 'http://my-custom-dicom-server/dicom.cgi'
    output_text = await structured_report_to_html_async(test_file_path,
      url_prefix=url_prefix,
      css_reference="https://css-host/dir/subdir/my-first-style.css")
    assert output_text.find(url_prefix) != -1
    assert output_text.find('http://localhost/dicom.cgi') == -1
    assert output_text.find('<link rel="stylesheet" type="text/css" href="https://css-host/dir/subdir/my-first-style.css">') != -1

    test_css_file_path = 'test-style.css'
    output_text = await structured_report_to_html_async(test_file_path, css_file=test_css_file_path)

    assert output_text.find('<style type="text/css">') != -1
    assert output_text.find('background-color: lightblue;')
    assert output_text.find('margin-left: 20px;') != -1
    assert output_text.find('</style>') != -1
    assert output_text.find('http://my-custom-dicom-server/dicom.cgi') == -1
    assert output_text.find('http://localhost/dicom.cgi') != -1
