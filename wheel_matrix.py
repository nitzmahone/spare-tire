#!/usr/bin/env python
"""Generate the FreeBSD wheel matrix to simplify maintenance."""

from __future__ import annotations

import dataclasses
import pathlib

import yaml


@dataclasses.dataclass
class Package:
    name: str
    versions: list[str]
    abi: str = ''


def main() -> None:
    freebsd_pythons = {
        '12.4': ['3.9'],
        '13.2': ['3.9', '3.11'],
    }

    packages = [
        Package(name='bcrypt', versions=['latest'], abi='abi3'),
        Package(name='cryptography', versions=['40.0.1', 'latest'], abi='abi3'),
        Package(name='cffi', versions=['latest']),
        Package(name='coverage', versions=['6.5.0', 'latest']),
        Package(name='lazy-object-proxy', versions=['latest']),
        Package(name='MarkupSafe', versions=['2.0.0', '2.1.2', 'latest']),
        Package(name='PyYAML', versions=['6.0', 'latest']),
    ]

    architectures = dict(
        amd64='x86_64',
        arm64='aarch64',
    )

    data = dict(
        packages=(matrix_packages := {}),
    )

    for package in packages:
        matrix_packages[package.name] = dict(versions=(matrix_versions := {}))

        for version in package.versions:
            matrix_versions[version] = dict(wheels=(matrix_wheels := []))

            for arch_label, arch in architectures.items():
                for freebsd_version, pythons in freebsd_pythons.items():
                    if package.abi:
                        pythons = pythons[:1]  # packages with ABI builds only need to support the lowest Python version

                    for python in pythons:
                        matrix_python = dict(tag=f'cp{python.replace(".", "")}')

                        if package.abi:
                            matrix_python.update(abi=package.abi)

                        matrix_wheels.append(dict(
                            platform_tag=f'freebsd_{freebsd_version.replace(".", "_")}_release_{arch_label}',
                            platform_instance=f'freebsd/{freebsd_version}',
                            platform_arch=arch,
                            python=[
                                matrix_python,
                            ],
                        ))

    with pathlib.Path('wheel_matrix.yml').open('w') as matrix_file:
        print(f'# This file was generated by the `{pathlib.Path(__file__).name}` script.', file=matrix_file)

        yaml.safe_dump(data, matrix_file, sort_keys=False)


if __name__ == '__main__':
    main()
