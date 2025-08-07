
import os
from pathlib import Path

from setuptools import find_namespace_packages, setup



# Declare your non-python data files:
# Files underneath configuration/ will be copied into the build preserving the
# subdirectory structure if they exist.
data_files = []
for root, dirs, files in os.walk("configuration"):
    data_files.append(
        (os.path.relpath(root, "configuration"), [os.path.join(root, f) for f in files])
    )



setup(
    name="sagemaker_studio_boto3_plugin",
    version="0.0.1",
    author="Amazon Web Services",
    description="SageMaker Studio Boto3 Plugin",
    long_description="This is a SageMaker Studio Boto3 plugin to allow access to LakeFormation governed table",
    long_description_content_type="text/markdown",
    data_files=data_files,
    packages=find_namespace_packages(where="src"),
    package_dir={
        "sagemaker_studio_boto3_plugin": "src/sagemaker_studio_boto3_plugin",
    },
    python_requires=">=3.9",
    tests_require=["pytest"],
    test_suite="test",
    extras_require={
        "test": ["pytest", "pytest-cov", "toml", "coverage"],
        "dev": ["wheel", "invoke", "twine"],
    },
)
