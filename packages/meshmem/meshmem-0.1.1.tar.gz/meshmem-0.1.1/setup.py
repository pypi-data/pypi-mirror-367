from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="meshmem",
    version="0.1.1",  # <-- Increment this for every PyPI release!
    description="MeshMem SDK – Protocol-native, auditable, and composable cognitive memory for AI and multi-agent systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Hongwei Xu, Consenix Labs Ltd",
    author_email="hongwei@consenix.com",
    url="https://meshmem.io",
    license="SEE LICENSE FILE",
    license_files=["LICENSE", "IP_NOTICE.md"],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.23",
        "tqdm",
        "openai",         # Remove if you want pure local
        "python-dotenv",  # For loading .env in examples
    ],
    extras_require={
        "dev": [
            "pytest",
            "flake8",
            "black",
        ]
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    keywords="mesh memory, meshmem, cognitive memory, ai, multi-agent, protocol, SVAF, CMB",
    project_urls={
        "Documentation": "https://meshmem.io/docs",
        "Source": "https://github.com/meshmem/meshmem-sdk",
        "Bug Tracker": "https://github.com/meshmem/meshmem-sdk/issues",
        "Protocol Whitepaper": "https://consenix.com/papers/mesh-memory-white-paper"
    },
    # Custom legal/IP notice in description and license_files (see LICENSE/IP_NOTICE)
)
