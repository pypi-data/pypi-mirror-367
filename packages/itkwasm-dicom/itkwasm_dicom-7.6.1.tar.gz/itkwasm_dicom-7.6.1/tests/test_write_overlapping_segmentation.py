import pytest
import sys

if sys.version_info < (3,10):
    pytest.skip("Skipping pyodide tests on older Python", allow_module_level=True)

from pytest_pyodide import run_in_pyodide

from .fixtures import emscripten_package_wheel, package_wheel, input_data

@run_in_pyodide(packages=['micropip'])
async def test_write_overlapping_segmentation(selenium, package_wheel, emscripten_package_wheel):
    import micropip
    await micropip.install(emscripten_package_wheel)
    await micropip.install(package_wheel)

    from itkwasm_dicom import write_overlapping_segmentation

    # Write your test code here
