from setuptools import setup, find_namespace_packages

setup(
    name="llm-queue-task-manager",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    install_requires=[
        "redis>=4.0.0",
        "pydantic>=2.0.0",
    ],
)
