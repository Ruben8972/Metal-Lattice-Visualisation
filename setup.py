from setuptools import setup, find_packages

setup(
    name="metallgitter-visualisierung",
    version="0.2.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["numpy", "pyvista"],
    extras_require={"dev": ["pytest", "pyinstaller"]},
    entry_points={
        "console_scripts": ["metallgitter-vis=vis.main:main"],
        "gui_scripts": ["metallgitter-vis-gui=vis.main:main"],
    },
    python_requires=">=3.11",
)
