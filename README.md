# Activity Browser plugin : Template

An empty plugin to start from.

This repo contains the documentation to create Activity Browser plugins. It also build an empty Activity Browser plugin available on Anaconda. 

# Content

- [Activity Browser](#activity-browser)
- [Test this plugin](#test-this-plugin)
- [Creating a plugin](#creating-a-plugin)
    - [Creating the repository](#creating-the-repository)
    - [Adding metadata](#adding-metadata)
        - [Plugin infos](#plugin-infos)
        - [Deploy to anaconda](#deploy-to-anaconda)
    - [Testing](#testing)
- [Plugin system documentation](#plugin-system-documentation)
- [Guidelines](#guidelines)

# Activity Browser

[The activity browser](https://github.com/LCA-ActivityBrowser/activity-browser) is an open source software for Life Cycle Assessment (LCA) that builds on top of the [Brightway2](https://brightway.dev) LCA framework.

# Test this plugin

- activate your Activity Browser conda environment
- install this plugin with conda :

```
conda install -c pan6ora ab-plugin-template
```

- start Activity Browser
- Select the plugin in plugins list

# Creating a plugin

This document will guide you through the process of creating a plugin for Activity Browser.

## Creating the repository

- Go to [this repository main page](https://github.com/Pan6ora/ab-plugin-Template) and click on `Use this template`
- Give your project a name (ideally something like `ab-plugin-MyPlugin`)
- Check the `Include all branches` box
- Create the repository

Once the repository is created you should clone it locally.

The repo should contain 2 branches:
- `main` which is a real plugin named Template and contains this documentation
- `template` which is the branch to be completed with your project infos

After cloning the repository you need to set it up to start from the `template` branch. This can be done with the following git commands:

```
git checkout main
git reset --hard template
git push -f
git branch -d template
git push origin --delete template
```

You should now have only one branch called `main` and containing the content of the old branch `template`.

## Adding metadata

The repository already contains some files to get you started:

- `.github` and `ci` folders to deploy your plugin to Anaconda
- `ab_plugin_plugin_name` contains the plugin code
- `setup.py` file to create a python package
- basic CHANGELOG, LICENSE and README

Before starting to add functionalities to the plugin you need to fill some metadata.

### Plugin infos

Some keywords need to be changed in multiple files. The best way to doing that might be using a Search & Replace functionality in the project folder. These are keywords to change:

- `plugin_name` (4 results in 3 files)
- `one_line_description` (3 results in 2 files)
- `plugin_url`: replace by github url (3 results in 2 files)
- `plugin_author_email` (1 result in setup.py)
- `plugin_author` (1 result in setup.py)

The name of the code folder also needs to be changed with your plugin name.

### Deploy to Anaconda

In case you want to make your plugin available on the Anaconda repository you will need to set the appropriate repository secret on Github.

- Get an Anaconda token (with read and write API access) at anaconda.org/USERNAME/settings/access
- Add it to the Secrets of the Github repository as `CONDA_UPLOAD_TOKEN`

More infos about Anaconda deployment later.

## Testing 

A simple way to test your plugin is to use pip.

Open a terminal in your conda environment, go to your project folder and install your plugin in development mode with pip:

```
pip install -e .
```

Then start activity-browser and go to `Tools>Plugins` menu. Your plugin should appear in the list. Activate it and close the window. Two tabs should appear with your plugin name.

Once you've made some changes, restart Activity Browser to see the result.

## Adding content

Each plugin can add any content it wants into one left panel tab and one right panel tab.

While it seems logical for a plugin to use data and events from Activity Browser itself it is not necessary. On could create a totally different application and still deploy it as a plugin.

Following documentation will give you informations about the plugin structure and the way it can interact with Activity Browser.

See also the [guidelines](#guidelines) section to learn good practices.

# Plugin system documentation

This section is the documentation of the plugin system implemented in Activity Browser. It will hopefully help you to understand how to make your plugins work.

## Main characteristics

- A plugin is a conda package named ab-plugin-XXX
- A plugin can add any content in two tabs (Left/Right)
- Plugins connect to AB through signals
- Plugins can be selected per-project

## What a plugin can do

- adding content in the two tabs (sub-tabs, text, graphics...)
- adding wizards
- importing databases
- put stuff in the project folder
- connect to Activity Browser signals and generate them

## What a plugin can't do

- modifying other tabs or GUI parts

## Plugin content

**classes**

There are two main classes :

- `Plugin` is the main class defined in the init file of the plugin. It inherit from the `Plugin` class defined in Activity Browser.
- `PluginTab` is the mother class of every tabs the plugin will add to AB interface (one on each left/right panel).

**hooks**

The plugin class has 3 methods that are run by AB at a certain point :

- `load()` is run each time the plugin is added tp the project or reloaded. It kind of replaces the init method.
- `close()` is run when AB get closed.Put there the code to end your plugin properly.
- `remove()` is run when the plugin is removed from the current project. Use it to clean the place.

### Storage

**Plugins data**

Datas are added per-project. The plugin can add everything it needs in the project folder.

**Project plugins**

To keep track of plugins used in a project, an entry is added to project settings :

```json
/home/user/.local/share/Brigtway3/default.xxx/AB_project_settings.json
{
    "plugins_list": [
        "MyFirstPlugin",
        "MySecondPlugin"
    ],
    "read-only-databases": {
        "biosphere3": true,
        "Idemat": true
    }
}
```

# Guidelines

**Follow Activity Browser way of doing things**

We encourage you to follow th Activity Browser files tree structure and guidelines. This will help people working with it to understand your code.



## Hooks

The plugin class has 3 methods that are run by AB at a certain point :

- `load()` is run each time the plugin is added tp the project or reloaded. It kind of replaces the init method.
- `close()` is run when AB get closed.Put there the code to end your plugin properly.
- `remove()` is run when the plugin is removed from the current project. Use it to clean the place.
