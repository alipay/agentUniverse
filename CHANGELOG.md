# Changelog
**************************************
Language Version: [简体中文](CHANGELOG_zh.md) | [English](CHANGELOG.md)

This document records the version update history of the project.

## Version Number Format
The format of the version number is MAJOR.MINOR.PATCH, and the version number increment rule is as follows:
- MAJOR version when you make incompatible API changes,
- MINOR version when you add functionality in a backwards compatible manner,
- PATCH version when you make backwards compatible bug fixes.
- For more details, please refer to [Semantic Versioning 2.0.0](https://semver.org)

## Record Types
Init - Project initialization.
Added - Newly added features.
Changed - Changes to existing functionalities.
Deprecated - Soon to be deprecated features.
Removed - Features removed in this version.
Fixed - Any bug fixes.
Security - Patches and security improvements.
Note - Additional remarks regarding the version.

***************************************************

# Version Update History
## [0.0.5] - 2024-05-08
### Added
- The LLM component supports streaming calls.
- The Knowledge component has an added update definition.

### Fixed
- Fixed potential concurrency safety issues in the peer planner.
- Fixed the issue in version 0.0.4 of the PyPI package where the packaging method forced users to enter an AK upon startup.

### Note 
- Some code optimizations and documentation updates.

## [0.0.4] - 2024-04-26
### Added
- Add version management capability to the prompt.

### Fixed
- Fixed compatibility issues on Windows
  * Due to compatibility issues of Gunicorn with Windows systems, automatically identify the kernel version to select the web startup method.
  * Specified YAML reading as UTF-8 encoding method.

### Note
- [2024-05-08] Please be aware that the PyPI package version 0.0.4 includes the sample_standard_app example project by default. This will reference additional components from sample_standard_app at startup and require users to input an AK. If you are not using the corresponding components, you can bypass this restriction by using a mock AK. This issue has been fixed in version 0.0.5.

## [0.0.3] - 2024-04-19
### Init
- The official release version of AgentUniverse has been initialized. Enjoy using it!

## [0.0.2] - 2024-04-17
### Fixed
- Fixed an issue where associated dependencies were not being automatically installed when installing package versions.

## [0.0.1] - 2024-04-09
### Init
- Project initialization commit. This framework is a large model multi-agent framework. Enjoy using it!