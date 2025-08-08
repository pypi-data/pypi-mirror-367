# Textual-Pyfiglet Changelog

## [1.1.0] 2025-08-07

### Changed

- The `font` argument no longer uses the prebuilt fonts list to validate the font. Instead, it now uses the `FigletFont.preloadFont` method to check if the font exists. The validation will only fail if the font truly does not exist. It will now work for any fonts that are installed with other methods such as directly with Pyfiglet.
- The `fonts_list` class attribute has been changed to a property that calls `FigletFont.getFonts()` to scan for all currently available fonts. This list will now always be up to date with any fonts installed using any method.
- Changed the wording of the docstrings for the `font` property and the `set_font` method to clarify that they can accept any font installed with Pyfiglet, not just the built-in fonts, as well as a note about `set_font` being preferable for manually installed fonts.

### Added

- Added a new constructor argument `font_path` to the `FigletWidget` class. This allows you to specify a custom font path (str or Path object) to use for the widget. If this is set, it will install and set the font in one step, using the `FigletFont.install_font` method, thus avoiding the need to call `install_font` separately.
- Added new `FigletWidget.install_font` class method to install a font from a file path (str or Path object). This method is a wrapper over the Pyfiglet font installation method.

## [1.0.1] 2025-07-30

- Dropped the required Textual version back down to 3.7.1 (last 3.x.x release) to maintain compatibility with Textual 3.x.x.
- Made some changes to the demo to make the library compatible with Textual 3.x.x
- Added `/tests` directory with unit tests, a [pytest] section in `pyproject.toml`, and added `just test` command to the justfile.
- Added Nox testing and `noxfile.py` to run tests in different Python versions and across different versions of Textual.
- Added pytest, pytest-asyncio, and pytest-textual-snapshot to dev dependencies.
- Deleted `ci-requirements.txt` as it is no longer needed with the new Nox setup.
- Changed `ci-checks.yml` to run Nox instead of individual commands for MyPy, Ruff, Pytest, etc.

## [1.0.0] 2025-07-28

### Usage / API changes

- Promoted library to 1.0.0 / stable release.
- Upgraded to Textual 5.0.0.
- Removed Rich-Pyfiglet dependency, now using the new type-hinted Pyfiglet directly. This probably will not affect anybody.

### Code and project changes

- Renamed Changelog.md to CHANGELOG.md
- Added 2 workflow to .github/workflows:
  - ci-checks.yml - runs Ruff, MyPy, BasedPyright (will add Pytest later)
  - release.yml - Workflow to publish to PyPI and github releases
- Added 2 scripts to .github/scripts:
  - adds .github/scripts/validate_main.sh
  - adds .github/scripts/tag_release.py
- Added 1 new file to root: `ci-requirements.txt` - this is used by the ci-checks.yml workflow to install the dev dependencies.
- Added basedpyright as a dev dependency to help with type checking. Made the `just typecheck` command run it after MyPy and set it to 'strict' mode in the config (added [tool.basedpyright] section to pyproject.toml).
- Replaced build and publish commands in the justfile with a single release command that runs the two above scripts and then pushes the new tag to Github
- Workflow `update-docs.yml` now runs only if the `release.yml` workflow is successful, so it will only update the docs if a new release is made (Still possible to manually run it if needed, should add a 'docs' tag in the future for this purpose).
- Changed the `.python-version` file to use `3.9` instead of `3.12`.
- Deleted the CustomListView class as it is no longer necessary in Textual 5.0.0. (Textual added indexing to the ListView class).

## [0.10.0] 2025-07-24

- Potentially Breaking Change: Updated to the new Rich-Pyfiglet 0.2.0. This new version is no longer a fork of Pyfiglet, but instead uses the Pyfiglet library as a dependency (My essential changes got merged back upstream, so having a fork is no longer necessary! Major win). Things should mostly work as expected, but there may be some minor API changes or fonts that are no longer there. This can potentially break some apps that were using the old Rich-Pyfiglet API, but I have tried to keep the changes minimal.

## 0.9.2 (2025-06-22)

- Updated to use the new ColorOMatic 0.2.0. Everything works as expected and there should be no breaking or API changes.
- Refactored the demo code slightly to be more similar to the ColorOMatic demo. Nested all CSS in demo/styles.tcss to improve readability.

## 0.9.1 (2025-06-22)

- Changed the ColorOMatic dependency version from >=0.1.4 to ==0.1.4. This was done because the ColorOMatic underwent a major overhaul and internal refactor, and I need to ensure that the FigletWidget is compatible with the new ColorOMatic before I allow it to use the new version.

## 0.9.0 - Color-O-Matic major split update (2025-06-15)

- The color and animation system was split off to its own package. Textual-Pyfiglet now uses Textual-Color-O-Matic as a dependency. This has reduced the amount of code in the Figletwidget.py module from over 800 lines (including all comments/blank lines) to just under 400. The API remains exactly the same and there should be no breaking changes.
- The demo app was refactored to be a subpackage split into several files for significantly better readability (Also matches the same demo structure as the Color-O-Matic package).

## 0.8.6 (2025-06-10)

- Fixed typo in pyproject.toml locking textual-slidecontainer to 0.4.0

## 0.8.5 (2025-06-06)

- Fixed bug where some small fonts caused a division by zero error
- Updated the project to use the new rich-pyfiglet 0.1.4, which uses the new type hints added into Pyfiglet, making all of the type: ignore statements no longer necessary and thus were removed.

## 0.8.4 (2025-05-22)

- Improved some docstrings to reflect new features, added a docstring for FigletWidget.fonts_list

## 0.8.3 (2025-05-22)

- Added ability to detect textual CSS theme variables ($primary, $secondary, $panel, etc) which are passed in to the color list.
- Added detection for app theme changes, so if you have a CSS theme variable passed in to the color list, it will automatically change to match the new theme. This allows for dynamically-colored widgets which will change their color to match the current theme.
- The animate button in the demo will now be disabled whenever there's less than 2 colors in the color list.

## 0.8.2 (2025-05-22)

- Fixed bug when initializing the widget with 2 or more colors in the list.
- Fixed bug when initializing the widget with only 1 color and setting animate to true.

## 0.8.0 (2025-05-15)

Enhanced the color and animation system in several ways:

- BREAKING CHANGE - The color system has been upgraded to using a list that can take any number of colors instead of using variables color1 and color2. As such, color1 and color2 have been removed. There is now only the `colors` constructor parameter and corresponding `color_list` variable. This now matches the rich_pyfiglet library (which also takes colors as a list). If you were passing color1 and color2 in to the constructor, simply modify your app to pass them both in as a list. The set_color1 and set_color2 methods were likewise replaced with a single set_color_list method. (You can set the reactive directly, but since it is a list you would also need to use the mutate_reactive method in Textual.)
- BREAKING CHANGE - The `animation_speed` parameter was changed to `fps` and correspoding `animation_fps` reactive. It also had an 'auto' mode added to it. This number is still a float, but existing code will need to be slightly modified. FPS is more intuitive and matches the rich_pyfiglet library's API. When in auto mode, it will use 12 FPS for gradient animation, 8 FPS for smooth_strobe, and it will drop to 1 fps if the animation type is changed to 'fast_strobe'.
- Added `animation_type` argument and corresponding reactive attribute of the same name. Can now choose between gradient, smooth_strobe, and fast_strobe. Note that smooth_strobe and fast_strobe will ignore the horizontal bool (they don't have a direction). Added a corresponding `set_animation_type` method to go along with the new animation_type attribute.
- Addded `horizontal` argument and corresponding reactive attribute. This bool will make the gradient render horizontally instead of vertically. In auto mode it will adjust to the length of the widget.
- Added `reverse` argument and corresponding reactive attribute. This bool will make the running animation go in reverse. For vertical gradients this toggles between up and down. For horizontal gradients this toggles between left and right. With the strobe effects, this will make the colors run in the reverse order.
- Enhanced the demo to show all these new settings.

## 0.7.0 - The major split update (2025-05-13)

- Pyfiglet was removed as a subpackage, and moved over to the newly created Rich-Pyfiglet library. Rich-Pyfiglet is now a dependency of Textual-Pyfiglet and provides the Pyfiglet fork.
- Re-worked much of the API and public facing methods. Made it much easier to modify most of the reactives directly. Added docstrings to all the public reactives.
- Added validation methods to most of the reactives (using Textual's built in reactive validators).
- Gradients in 'auto' mode will now automatically re-calculate when the widget's height changes.
- If one of the colors is removed while animating, it will now stop the animation internally.
- Enhanced type hinting: Package now passes MyPy and Pyright in strict mode.
- Added py.typed file to mark package as typed for Pyright/MyPy.
- Added a small example.py file into the package.
- Colors passed in are now only parsed one time by the validator method, because its an expensive call.
- Several small bug fixes in demo app.
- Added Ruff, Black, and MyPy to project dev dependencies, and set all of them to run automatically using the justfile before publishing.

## 0.6.0 - The Animation update (2025-04-22)

- Color, gradient, and animation modes have been added. There are 5 new arguments in the constructor:
  - color1
  - color2
  - animate: Boolean to toggle on/off
  - animation_quality: Auto mode uses the figlet height by default.
  - animation_interval: Speed in seconds as a float.
- The fonts list is now a string literal collection to give auto-complete. Choosing a font is now much easier.
- The full fonts collection is now included by default. Deleted the extended fonts package from PyPI. This should also solve any issues with PyInstaller or other packaging tools.
- Much of the widget was re-written from the ground up to switch to using the LineAPI.
- Platformdirs has been removed as a dependency. (Now there's no dependencies.)
- Completely revamped the demo. Added Textual-Slidecontainer for the menu bar. Also added new options to show off the color and animation features.
- Changed package manager and build system from Poetry to uv
- Converted Makefile into Justfile
- Deleted config.py and other code related to managing the fonts (no longer needed).
- Removed Inner/Outer architecture, decided it was overcomplicating things. Converted it to one large class.
- Added a help section for the demo.
- Added a `figlet_quick` class method onto FigletWidget which is a bridge to `pyfiglet.figlet_format`

## 0.5.5(2024-11-16)

- Fixed bug caused by Textual 0.86 renaming arg in Static widget.

## 0.5.2 (2024-11-01)

- Fixed typo in README.md

## 0.5.1 (2024-10-29)

- Fixed all wording in docstings that weren't up to date

## 0.5.0 (2024-10-29)

- Switched fonts folder to user directory using platformdirs
- Added platformdirs as dependency.
- Switched the _InnerFiglet to use reactives
- Added a Justify option and set_justify method
- Added return_figlet_as_string method

## 0.4.2 (2024-10-26)

- Added copy text to clipboard button
- Fixed bug with starting text
- Updated text showing container sizes to reflect the new inner/outer system

## 0.4.0 (2024-10-26)

- Enormous improvement to container logic with inner/outer containers.
- Fixed up docstrings in numerous places
- Updated readme to reflect changes in usage

## 0.3.5 (2024-10-25)

- Fixed dependency problems in pyproject.toml
- Fixed some mistakes in documentation
- Cleaned up unused code

## 0.3.2 (2024-10-24)

- Fixed 2 bugs in config.py
- Wrote a full usage guide
- Moved list scanning logic to figletwidget.py

## 0.2.0 (2024-10-23)

- Fixed the resizing issue
- Greatly improved the demo again
- Moved CSS to a separate file

## 0.1.2 (2024-10-22)

- Significantly improved the demo.
- Swapped some fonts
- Expanded makefile
- Created base fonts backup folder

## 0.1.0 (2024-10-22)

Start of Textual-Pyfiglet project. Main changes:

- Fork of PyFiglet. Git history of PyFiglet is maintained.
- Switched build tools to Poetry.
- Removed almost all fonts, leaving only 10 (moved to asset pack, see below)
- pyfiglet folder moved to inside textual_pyfiglet
- removed tools folder. (Scripts for running the CLI, not needed anymore)
- Command line tool to run the original demo is added to the makefile
- 519 fonts moved to asset pack: textual-pyfiglet-fonts
  Asset pack is installed by: pip install textual-pyfiglet[fonts]