from setuptools import setup, find_packages

setup(
    name="apache-airflow-providers-onehouse",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "apache-airflow>=2.9.2",
    ],
    python_requires=">=3.10",
    author="OneHouse",
    author_email="",
    description="Apache Airflow Provider for OneHouse",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    classifiers=[
        "Framework :: Apache Airflow",
        "Framework :: Apache Airflow :: Provider",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    entry_points={
        "apache_airflow_provider": [
            "provider_info=airflow_providers_onehouse.__init__:get_provider_info"
        ]
    },
    project_urls={
        "Bug Tracker": "https://github.com/onehouseinc/airflow-providers-onehouse/issues",
        "Source Code": "https://github.com/onehouseinc/airflow-providers-onehouse",
    },
    keywords=["airflow", "onehouse", "provider"],
) 