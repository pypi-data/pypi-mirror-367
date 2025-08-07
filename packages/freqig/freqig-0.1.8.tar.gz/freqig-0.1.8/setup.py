from setuptools import setup, find_packages

setup(
    name="freqig",
    version="0.1.8",
    packages=find_packages(),
    install_requires=[
        'torch>=2.0.0',
        'numpy>=1.21.0',
        'captum>=0.6.0',
    ],
    extras_require={
        'convert': [
            'onnx',
            'tf2onnx',
            'onnx2pytorch',
        ],
        'academic': ['howfairis>=0.20.0']
    },
    author="Paul Gräve",
    description="Frequency-domain model explanation (IG) package",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url="https://gitlab.com/paulabraham.graeve/flex",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    license="MIT",
    license_files=["LICENSE", "CITATION.cff"],
)