from setuptools import find_packages, setup

# ToDo: needs a patch to ignore the requirements definition during the build process of the Debian package
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
        "frida-scripts/*.js",
        "frida-dynamic-hooks/*.js",
        "drop_server/templates/*.html",
    ]},
    zip_safe=True,
    entry_points={
        "console_scripts": [
            "pirogue-intercept-tls = pirogue_evidence_collector.entrypoints.intercept_gated:start_interception",
            "pirogue-intercept-single = pirogue_evidence_collector.entrypoints.intercept_single:start_interception",
            "pirogue-intercept-gated = pirogue_evidence_collector.entrypoints.intercept_gated:start_interception",
            "pirogue-view-tls = pirogue_evidence_collector.entrypoints.view_tls:view_decrypted_traffic",
            "pirogue-android = pirogue_evidence_collector.entrypoints.pirogue_android:main",
            "pirogue-file-drop = pirogue_evidence_collector.entrypoints.pirogue_file_drop:main",
            "pirogue-extract-metadata = pirogue_evidence_collector.entrypoints.pirogue_extract_metadata:main",
            "pirogue-timestamp = pirogue_evidence_collector.entrypoints.pirogue_timestamp:main"
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL-3.0 License",
        "Operating System :: OS Independent",
    ],
)
