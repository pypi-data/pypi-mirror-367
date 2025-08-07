from setuptools import setup, find_packages

setup(
    name="soai-setup",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'soai-setup=soai_setup.cli:main',
        ],
    },
    author="Akshayy06",
    author_email="yaraakshaykumar22@gmail.com",
    description="SoAI 2025 internship tech stack installer CLI tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://code.swecha.org/Akshay06/soai-2025.techstack-setup.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
