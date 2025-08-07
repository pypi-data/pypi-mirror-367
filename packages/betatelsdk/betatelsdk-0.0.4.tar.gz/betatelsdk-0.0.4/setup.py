from setuptools import setup, find_packages

VERSION = '0.0.4'
DESCRIPTION = 'An SDK for Betatel services'
LONG_DESCRIPTION = 'An SDK for Betatel services'

setup(
    name="betatelsdk",
    version=VERSION,
    author="Betatel LTD",
    author_email="<muhamed.b@beta.tel>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["requests"],
    keywords=['python', 'tts', 'tele', 'voice', 'sms', 'sip', 'call', 'betatel'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)