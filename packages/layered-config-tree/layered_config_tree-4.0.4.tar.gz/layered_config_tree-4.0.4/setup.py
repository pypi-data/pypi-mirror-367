import json
import sys
from pathlib import Path

from packaging.version import parse
from setuptools import find_packages, setup

with open("python_versions.json", "r") as f:
    supported_python_versions = json.load(f)

python_versions = [parse(v) for v in supported_python_versions]
min_version = min(python_versions)
max_version = max(python_versions)
if not (
    min_version <= parse(".".join([str(v) for v in sys.version_info[:2]])) <= max_version
):
    py_version = ".".join([str(v) for v in sys.version_info[:3]])
    # NOTE: Python 3.5 does not support f-strings
    error = (
        "\n----------------------------------------\n"
        "Error: Layered Config Tree runs under python {min_version}-{max_version}.\n"
        "You are running python {py_version}".format(
            min_version=min_version.base_version,
            max_version=max_version.base_version,
            py_version=py_version,
        )
    )
    print(error, file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    base_dir = Path(__file__).parent
    src_dir = base_dir / "src"

    about: dict[str, str] = {}
    with (src_dir / "layered_config_tree" / "__about__.py").open() as f:
        exec(f.read(), about)

    with (base_dir / "README.rst").open() as f:
        long_description = f.read()

    install_requirements = [
        "vivarium_dependencies[pyyaml]",
        "vivarium_build_utils>=2.0.1,<3.0.0",
    ]
    setup_requirements = ["setuptools_scm"]
    test_requirements = [
        "vivarium_dependencies[pytest]",
    ]
    doc_requirements = [
        "vivarium_dependencies[sphinx,sphinx-click,ipython,matplotlib]",
        "sphinxcontrib-video",
    ]
    interactive_requirements = [
        "vivarium_dependencies[interactive]",
    ]
    dev_requirements = [
        "vivarium_dependencies[lint]",
        # typing extensions
        "types-setuptools",
    ]

    setup(
        name=about["__title__"],
        description=about["__summary__"],
        long_description=long_description,
        license=about["__license__"],
        url=about["__uri__"],
        author=about["__author__"],
        author_email=about["__email__"],
        classifiers=[
            "Intended Audience :: Developers",
            "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
            "Natural Language :: English",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: POSIX",
            "Operating System :: POSIX :: BSD",
            "Operating System :: POSIX :: Linux",
            "Operating System :: Microsoft :: Windows",
            "Programming Language :: Python",
            "Programming Language :: Python :: Implementation :: CPython",
            "Topic :: Software Development :: Libraries",
        ],
        package_dir={"": "src"},
        packages=find_packages(where="src"),
        include_package_data=True,
        install_requires=install_requirements,
        tests_require=test_requirements,
        extras_require={
            "docs": doc_requirements,
            "interactive": interactive_requirements,
            "test": test_requirements,
            "dev": doc_requirements
            + interactive_requirements
            + test_requirements
            + dev_requirements,
        },
        zip_safe=False,
        use_scm_version={
            "write_to": "src/layered_config_tree/_version.py",
            "write_to_template": '__version__ = "{version}"\n',
            "tag_regex": r"^(?P<prefix>v)?(?P<version>[^\+]+)(?P<suffix>.*)?$",
        },
        setup_requires=setup_requirements,
    )
