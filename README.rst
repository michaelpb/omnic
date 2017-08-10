.. figure:: docs/images/logo_medium.png
   :alt: OmniC Logo

Omni Converter
==============

.. figure:: https://travis-ci.org/michaelpb/omnic.svg?branch=master
   :alt: Travis CI

Mostly stateless microservice for generating on-the-fly thumbs and previews of
a wide variety of file types. Comes battery-included, but designed like a
framework to be extended into any arbitrary conversion pipelines.

Omni Converter (which can be shortened to OmniC or ``omnic``) is free software,
licensed under the GPL 3.0.

- **WIP WARNING:** OmniC is still 'unreleased software', a work in progress.
  The API is subject to rapid change. I intend to release the first stable
  version before the end of this year (2017).

What is OmniC?
==============

OmniC can do a lot of things. Most likely you will want it for making
visualizations and thumbnails without (any other) backend code.  It is inspired
in part by [White
Noise](http://whitenoise.evans.io/en/stable/#infrequently-asked-questions).


On-the-fly conversions
----------------------

- OmniC is a web server that listens to requests like
  ``/media/thumb.png:200x200/?url=mysite.com/myimage.jpg``, and then it will
  download the `myimage.jpg` file, generate a 200x200 thumbnail of it, then
  respond with that thumbnail.

- It can also do filetype conversions like
  ``/media/PDF/?url=mysite.com/mydoc.doc`` for a PDF representation of a
  ``.doc`` file.

- OmniC doesn't reinvent any wheels, instead provides the framework to stitch
  together existing CLI converters and expose them as a microservice

Extensible conversion graph
---------------------------
- OmniC is written as both a "batteries included" micro-service that you can
  run as-is, and as a general web media framework

- Central to OmniC is the "Conversion Graph": **you give the URL to a file, and
  the desired type, and it finds the shortest path**  even if it takes multiple
  conversions

- OmniC's builtin converters can handle hundreds of file-types in many
  different use domains, including 3D files, documents, and more -- but if
  that's not enough, **it only takes a few lines to add your own converter**

Caching
-------

- Since conversion is slow, **every step is cached** so it is only done once,
  and in production it should sit behind an upstream cache or CDN

- OmniC thus potentially can replace worker/queue systems with a much simpler
  solution, **making dev environments far simpler** while resembling
  production, and **potentially reducing worker/queue scaling problems to load
  balancing problems**

Replacing the build step
------------------------
- OmniC's concept of conversion is extremely broad and versatile: For example,
  it can build minified JS bundles from ES6 sources

- Ideally, OmniC could replace most of the build-step during production
  deployments, making launches simply deploying new code to app servers, and
  everything else gets done as-needed on the first request (such as by a tester
  on staging)

JavaScript framework
--------------------
- OmniC comes with some JS to smooth over the experience: For uncached media,
  it will initially serve a placeholder, but with the included JS snippet it
  will reload the relevant assets when the conversion is finished

- OmniC also provides an **optional JavaScript viewer system**, hooked right
  into its conversion system: For example, a Word document might initially show
  as a JPG thumbnail, then on click show a PDF-based viewer in a modal

Docker
======

This repo provides a (very bulky) Dockerfile for working with OmniC. The
advantage is you don't have to worry about tracking down system dependencies to
take advantage of the built-in conversion graph.

1. Install and configure docker on your machine

2. Build the image: `docker build .`

3. Run the image: `docker run -it -p 127.0.0.1:8080:8080 <IMAGE HASH>`

4. Go to http://127.0.0.1:8080/admin/ to see the admin interface demo

Run the test suite: `docker run -it <IMAGE HASH> py.test`

Admin
-----

From here you can paste in an URL to a resource, that OmniC will attempt
to display as a thumbnail. In this example an OBJ file (3D model format)
of a trumpet was pasted in, and a 200x200 thumbnail was generated:

.. figure:: docs/images/admin_conversion_view.jpg?
   :alt: Admin interface screenshot

To the right of the thumbnail it has an HTML snippet (the source-code of the
thumbnail to the left), and a button that will take you to the conversion graph
for that type:

.. figure:: docs/images/admin_graph_view.jpg?
   :alt: Admin graph screenshot

Installing with pip
===================

If you want to run it outside of Docker, you can simply install it directly on
your machine, provided you have at least Python 3.5 installed.  The first step
is installing the Python package:

::

    pip install omnic

If you intend to run the webserver, you will need to install a few extra
dependencies:

::

    pip install sanic jinja2 uvloop

Contributing
============

Setting up a dev environment
----------------------------

1. Install Python 3, including ``pip`` and ``venv``:

   -  On Debian-based distros:

      -  ``sudo apt-get install python3 python3-env python3-pip``

   -  On macOS, use something like ``brew``

2. Create a virtualenv. For example:

   -  ``mkdir -p ~/.venvs/``
   -  ``python3 -m venv ~/.venvs/omnic``

3. Activate virtualenv:

   -  ``source ~/.venvs/omnic/bin/activate``
   -  You will need to do this any time you want to work

4. Install dependencies:

   -  ``pip install -r requirements.txt``

5. Run test suite, should have 150+ tests pass:

   -  ``py.test``

6. Start the server:

   -  ``./bin/omnic runserver``
