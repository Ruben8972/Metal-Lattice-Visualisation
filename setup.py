from setuptools import setup, find_packages

setup(
    name="metal-lattice-visualisation",
    version="0.2.2",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["numpy", "pyvista"],
    extras_require={"dev": ["pytest", "pyinstaller"]},
    entry_points={
        "console_scripts": ["metal-lattice-vis=vis.main:main"],
        "gui_scripts": ["metal-lattice-vis-gui=vis.main:main"],
    },
    python_requires=">=3.11",
)
