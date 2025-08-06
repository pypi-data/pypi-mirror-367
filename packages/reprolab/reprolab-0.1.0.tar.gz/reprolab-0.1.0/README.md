# ReproLab

[![Github Actions Status](/workflows/Build/badge.svg)](/actions/workflows/build.yml)

One step closer to reproducible research

ReproLab is a JupyterLab extension that helps researchers create reproducible experiments by providing tools for:
- Experiment tracking and versioning
- Environment management and dependency freezing
- Data archiving and sharing
- Zenodo integration for publishing

## Requirements

- JupyterLab >= 4.0.0
- Python >= 3.9
- Node.js >= 16.0.0

## Quick Install

The easiest way to install ReproLab is using the provided installation script:

```bash
# Make the script executable (if needed)
chmod +x install.sh

# Run the installation script
./install.sh
```

## Manual Install

If you prefer to install manually:

```bash
# Install npm dependencies
npm install

# Build the extension
npm run build:prod

# Install the Python package
pip install -e .
```

## Usage

After installation, start JupyterLab:

```bash
jupyter lab
```

The ReproLab panel will appear in the left sidebar. You can use it to:

1. **Create Experiments**: Track and version your research experiments
2. **Manage Environments**: Create reproducible Python environments
3. **Archive Data**: Save and share your research data
4. **Publish to Zenodo**: Create packages ready for publication

## Uninstall

To remove the extension, execute:

```bash
pip uninstall reprolab
```

## Contributing

### Development install

Note: You will need NodeJS to build the extension package.

The `jlpm` command is JupyterLab's pinned version of
[yarn](https://yarnpkg.com/) that is installed with JupyterLab. You may use
`yarn` or `npm` in lieu of `jlpm` below.

```bash
# Clone the repo to your local environment
# Change directory to the reprolab directory
# Install package in development mode
pip install -e "."
# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite
# Rebuild extension Typescript source after making changes
jlpm build
```

You can watch the source directory and run JupyterLab at the same time in different terminals to watch for changes in the extension's source and automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
jlpm watch
# Run JupyterLab in another terminal
jupyter lab
```

With the watch command running, every saved change will immediately be built locally and available in your running JupyterLab. Refresh JupyterLab to load the change in your browser (you may need to wait several seconds for the extension to be rebuilt).

By default, the `jlpm build` command generates the source maps for this extension to make it easier to debug using the browser dev tools. To also generate source maps for the JupyterLab core extensions, you can run the following command:

```bash
jupyter lab build --minimize=False
```

### Development uninstall

```bash
pip uninstall reprolab
```

In development mode, you will also need to remove the symlink created by `jupyter labextension develop`
command. To find its location, you can run `jupyter labextension list` to figure out where the `labextensions`
folder is located. Then you can remove the symlink named `reprolab` within that folder.

### Packaging the extension

See [RELEASE](RELEASE.md)
