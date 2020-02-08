import setuptools

setuptools.setup(
    name="rae",
    version="0.1",
    py_modules=["api_rae"],
    install_requires=["Typer"],
    entry_points="""
        [console_scripts]
        rae=api_rae:app
    """,
)
