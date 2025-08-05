from setuptools import setup

setup(
    name="sap-gui-library",  
    version="0.1.3",
    description="Facilitating interaction with the SAP GUI system",
    long_description=open("README.md", "r").read(), 
    long_description_content_type="text/markdown",  
    author="Felipe Chaparro", 
    author_email="felipelopezchaparro@gmail.com",  
    url="https://github.com/Chaparroo/sap-gui-library", 
    packages=["sap_gui_library"], 
    install_requires=[ 
        "pandas>=2.2.2",
        "numpy>=2.1.1",
        "python-dateutil==2.9.0.post0",
        "pytz==2024.2",
        "pywin32==306",
        "six==1.16.0",
        "tzdata==2024.1",
    ],
)
