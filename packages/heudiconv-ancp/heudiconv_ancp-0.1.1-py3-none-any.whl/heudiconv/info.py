__author__ = "HeuDiConv team and contributors"
__url__ = "https://github.com/nipy/heudiconv"
__packagename__ = "heudiconv"
__description__ = "Heuristic DICOM Converter"
__license__ = "Apache 2.0"
__longdesc__ = """
## About this fork

This is **not the official version of HeuDiConv**.  
It is a customized fork developed at the *Applied Neurocognitive Psychology Lab*, aimed at improving compatibility and usability in specific workflows.

In particular, this variant offers **full support for Windows environments** and **removes file-writing restrictions** present in the original version, making it more flexible for local pipelines and GUI-based tools.

All credits for the original development go to the NiPy community. This version is provided under the same [Apache 2.0 License](LICENSE) and is intended for specialized use cases.


Convert DICOM dirs based on heuristic info - HeuDiConv
uses the dcmstack package and dcm2niix tool to convert DICOM directories or
tarballs into collections of NIfTI files following pre-defined heuristic(s)."""

CLASSIFIERS = [
    "Environment :: Console",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering",
    "Typing :: Typed",
]

PYTHON_REQUIRES = ">=3.9"

REQUIRES = [
    # not usable in some use cases since might be just a downloader, not binary
    # 'dcm2niix',
    "dcmstack>=0.8",
    "etelemetry",
    "filelock>=3.0.12",
    "nibabel>=5.3.1",
    "nipype-ancp",
    "pydicom >= 1.0.0",
]

TESTS_REQUIRES = [
    "pytest",
    "tinydb",
    "inotify",
]

MIN_DATALAD_VERSION = "0.13.0"
EXTRA_REQUIRES = {
    "tests": TESTS_REQUIRES,
    "extras": [
        "duecredit",  # optional dependency
    ],  # Requires patched version ATM ['dcmstack'],
    "datalad": ["datalad >=%s" % MIN_DATALAD_VERSION],
}

# Flatten the lists
EXTRA_REQUIRES["all"] = sum(EXTRA_REQUIRES.values(), [])
