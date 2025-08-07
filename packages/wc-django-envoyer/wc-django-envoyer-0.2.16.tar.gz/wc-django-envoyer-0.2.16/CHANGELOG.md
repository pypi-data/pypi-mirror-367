# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.16]
### Added
- Indexes for all storable objects.

## [0.2.15]
### Fixed
- Channel config `is_active` parameter admin field.

## [0.2.14]
### Added
- Channel config `is_active` parameter to be able to disable channel at any time without deleting configuration.

## [0.2.13]
### Changed
- Template legend extended with an additional column with template-language key representation.

## [0.2.9]
### Fixed
- Attached users translations and admin.

## [0.2.8]
### Added
- Ability to attach `auth.User` users to messages with `wcd_envoyer.contrib.attached_users`.
-
## [0.2.7]
### Added
- Scheduled message sending using `wcd_envoyer.contrib.scheduled`.

## [0.2.3]
### Added
- Messages use the same form as templates for data field.

## [0.2.2]
### Added
- Errors tracking.

## [0.2.0]
### Added
- Celery sender.
### Fixed
- API improvements.

## [0.1.0]
Initial version.
