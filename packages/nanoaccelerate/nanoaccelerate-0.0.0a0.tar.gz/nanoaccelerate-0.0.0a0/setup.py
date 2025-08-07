# Copyright 2025 Zach Mueller. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import find_packages, setup


extras = {}
extras["quality"] = [
    "black ~= 23.1",  # hf-doc-builder has a hidden dependency on `black`
    "ruff ~= 0.11.2",
]

setup(
    name="nanoaccelerate",
    version="0.0.0a",
    description="mini-accelerate",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    keywords="deep learning",
    license="Apache",
    author="Zach Mueller",
    author_email="walkwithcode@gmail.com",
    url="https://github.com/muellerzr/nanoaccelerate",
    package_dir={"": "src"},
    packages=find_packages("src"),
    entry_points={
        "console_scripts": [
        ]
    },
    python_requires=">=3.9.0",
    install_requires=[
        "numpy>=1.17,<3.0.0",
        "packaging>=20.0",
        "psutil",
        "pyyaml",
        "torch>=2.0.0",
        "huggingface_hub>=0.21.0",
        "safetensors>=0.4.3",
    ],
    extras_require=extras,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)

# Release checklist
# 1. Checkout the release branch (for a patch the current release branch, for a new minor version, create one):
#      git checkout -b vXX.xx-release
#    The -b is only necessary for creation (so remove it when doing a patch)
# 2. Change the version in __init__.py and setup.py to the proper value.
# 3. Commit these changes with the message: "Release: v<VERSION>"
# 4. Add a tag in git to mark the release:
#      git tag v<VERSION> -m 'Adds tag v<VERSION> for pypi'
#    Push the tag and release commit to git: git push --tags origin vXX.xx-release
# 5. Run the following commands in the top-level directory:
#      make prepare_release
# 6. Upload the package to the pypi test server first:
#      make target=testpypi upload_release
# 7. Check that you can install it in a virtualenv by running:
#      make install_test_release
#      accelerate env
#      accelerate test
# 8. Upload the final version to actual pypi:
#      make target=pypi upload_release
# 9. Add release notes to the tag in github once everything is looking hunky-dory.
# 10. Go back to the main branch and update the version in __init__.py, setup.py to the new version ".dev" and push to
#     main.