import setuptools
import os

# Read the README.md for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Function to find all files in the frontend build directory
def get_frontend_files():
    files = []
    # Start walking from the package's root directory
    for (dirpath, dirnames, filenames) in os.walk("streamlit_contrib_clipboard/frontend/build"):
        # Create a relative path from the package root
        rel_dir = os.path.relpath(dirpath, "streamlit_contrib_clipboard")
        for file in filenames:
            files.append(os.path.join(rel_dir, file))
    return files

setuptools.setup(
    name="streamlit-contrib-clipboard",
    version="0.1.5", # Final version
    author="Omkar Pramod Hankare",
    author_email="ompramod9921@gmail.com",
    description="A Streamlit component to copy text to clipboard, even in iframed apps.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/om-pramod/streamlit-contrib-clipboard",
    license="MIT",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        "streamlit>=1.20.0",
    ],
    package_data={
        "streamlit_contrib_clipboard": get_frontend_files(),
    },
)