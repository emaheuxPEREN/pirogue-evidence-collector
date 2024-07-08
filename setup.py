from setuptools import find_packages, setup

requirements = [i.strip() for i in open("requirements.txt").readlines()]

setup(
    name="pirogue-evidence-collector",
    version="1.0.0",
    author="U+039b",
    author_email="hello@pts-project.org",
    description="A set of tools to collect evidence from mobile devices",
    url="https://github.com/PiRogueToolSuite/pirogue-evidence-collector",
    install_requires=requirements,
    packages=find_packages(),
    package_data={"pirogue_evidence_collector": [
        "frida-scripts/*.js"
    ]},
    zip_safe=True,
    entry_points={
        "console_scripts": [
            "pirogue-intercept-tls = pirogue_evidence_collector.entrypoints.intercept_single:start_interception",
            "pirogue-intercept-single = pirogue_evidence_collector.entrypoints.intercept_single:start_interception",
            "pirogue-intercept-gated = pirogue_evidence_collector.entrypoints.intercept_gated:start_interception",
            "pirogue-view-tls = pirogue_evidence_collector.entrypoints.view_tls:view_decrypted_traffic",
            "pirogue-android = pirogue_evidence_collector.entrypoints.pirogue-android:main",
            "pirogue-filedrop-server = pirogue_evidence_collector.entrypoints.pirogue-filedrop-server:main",
            "pirogue-save-metadata = pirogue_evidence_collector.entrypoints.pirogue-save-metadata:main",
            "pirogue-timestamp = pirogue_evidence_collector.entrypoints.pirogue-timestamp:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL-3.0 License",
        "Operating System :: OS Independent",
    ],
)
