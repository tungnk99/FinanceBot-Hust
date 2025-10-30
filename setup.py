from setuptools import setup, find_packages


def read_long_description() -> str:
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "FinanceBot agent libraries"


def read_requirements() -> list:
    requirements = []
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                requirements.append(line)
    except Exception:
        pass
    return requirements


setup(
    name="agent_libs",
    version="0.1.0",
    description="FinanceBot agent libraries",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    author="FinanceBot",
    python_requires=">=3.9",
    packages=find_packages(include=["agent_libs", "agent_libs.*"]),
    include_package_data=True,
    install_requires=read_requirements(),
)


