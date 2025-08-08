from setuptools import setup, find_packages

setup(
    name="rkguiv3",
    version="0.1.1",  # Увеличьте версию
    description="Comprehensive Tkinter-based GUI library",
    author="1001015dhh",
    license="MIT",
    packages=find_packages(include=['rkguiv3', 'rkguiv3.*']),  # Ключевое исправление
    include_package_data=True,
    package_data={
        'rkguiv3': ['*.py', 'widgets/*.py', 'dialogs/*.py', 'utils/*.py']
    },
    install_requires=[
        "pillow",
        "tkcalendar",
        "python-vlc",
        "cefpython3; platform_system=='Windows'",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
    ],
    keywords="tkinter gui widgets ui toolkit",
    python_requires=">=3.7",
)