from setuptools import setup, find_packages

setup(
    name="mentors-event-hub",
    version="0.1.0",
    author="Mentorstec",
    author_email="diego@mentorstec.com.br",
    description="Event hub for centralized exception logging and monitoring",
    long_description="Event hub for centralized exception logging and monitoring with Azure Service Bus support",
    url="https://github.com/mentorstec/mentors-event-hub",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "azure-servicebus>=7.0.0",
    ],
)