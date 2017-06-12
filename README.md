# WIP

*Nothing to see here, a work in progress!*


# Omni-Converter - omnic

![Travis CI](https://travis-ci.org/michaelpb/omnic.svg?branch=master)

Mostly stateless microservice for generating on-the-fly thumbs and previews of
a wide variety of file types.

Fully extendable to create any arbitrary conversion pipelines.

# Installation

**NOTE: Only Python 3.5+ is supported.**

The first step is simply installing the base python package:

`pip3 install omnic`

Depending on your needs, you will probably want to install a variety of other
system-level package conversion programs. This might include:

- `unoconv` - for converting many document formats
- `imagemagick` - for raster image conversion and manipulation
- `inkscape` - for vector conversion and manipulation

Additionally, converters specific to certain domains might be useful:

- `meshlab` - for converting between 3D model types
- `jsc3d` - for rendering 3D models in software (node npm package)
- `obabel` - for converting between chemical structure types
- `sdftosvg` - for rendering chemical structures (node npm package)


# Usage

There are 3 principle ways to use Omnic

## 1. Ready-to-use conversion web-server

The most common usage of Omnic is as a on-the-fly file format converter and
preview or thumb generator.

TODO: Stub

## 2. Media conversion server web-framework

Omnic is written in a very modular format, with a structure inspired partially
by Django. This allows you to tailor-make your own converters, using it as a
library, without forking. You can easily swap out any part, also.

TODO: Stub


## 3. Commandline file-format conversion sytem

While OmniConverter was written for the web, the server components are
optional. You can install without them. The handy `omnic` command is exposed in
the CLI to, thus exposing the power of

Omnic in this capacity functions simply as a web of very handy "glue" around
the other conversion programs used.

TODO: Stub



# Contributing

## Setting up a dev environment

It's much simpler to run a dev environment without Docker, just using
`virtualenv`, and using asyncio's task queueing. This might not precisely
resemble production environments, however it is very close.

1. Install Python 3, including `pip` and `venv`:
    * On Debian-based distros:
        * `sudo apt-get install python3 python3-env python3-pip`
    * On macOS, use something like `brew`
2. Create a virtualenv. For example:
    * `mkdir -p ~/.venvs/`
    * `python3 -m venv ~/.venvs/omnic`
3. Activate virtualenv:
    * `source ~/.venvs/omnic/bin/activate`
    * You will need to do this any time you want to work
4. Install dependencies:
    * `pip install -r requirements/local.txt`
5. (Optional) Run test suite:
    * `py.test`
6. Start the server:
    * `./bin/omnic runserver`


## Test routes

To test it, try visiting something like:
* http://localhost:8080/media/thumb.png:200x200/?url=unsplash.it/450/450

The first time you visit it it will just be a single placeholder pixel.
Subsequent times it should be 200x200 thumbnail

You might also be able to run this, if you have `unoconv` and ImageMagick
(providing the `convert` command) installed:
* `http://localhost:8080/media/thumb.jpg:200x200/?url=idee.org/Georgia_opposition_NATO-Eng-F.doc`

This will convert the `.doc` into a PDF, then into a JPG thumbnail

If you have `jsc3d` installed (a Node JavaScript based 3D model renderer), then
the following should render a delightful trumpet:
* `http://localhost:8080/media/thumb.jpg:200x200/?url=people.sc.fsu.edu/~jburkardt/data/obj/trumpet.obj`

The built-in converters interface with a variety of system binaries in order to
provide rendering and conversion of many document, image, mesh. Adding new
converters and rasterizers is simple, with relatively minimal code!

## Thx

* Used Nekroze' cookiecutter to start this package: https://github.com/Nekroze/cookiecutter-pypackage
