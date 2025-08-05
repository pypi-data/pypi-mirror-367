from setuptools import setup, find_packages

print("Packages found:", find_packages())  # 👈 Add this

setup(
    name='marcussays',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    author='Marcus McCrea',
    description='A fun and simple module by Marcus',
    long_description='A longer description of the marcussays module.',
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)