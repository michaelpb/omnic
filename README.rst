OmniC - Omni Converter
======================

.. figure:: https://travis-ci.org/michaelpb/omnic.svg?branch=master
   :alt: Travis CI

Mostly stateless microservice for generating on-the-fly thumbs and
previews of a wide variety of file types. Fully extendable to create any
arbitrary conversion pipelines.

Omni Converter (which can be shortened to OmniC or ``omnic``) is free
software, licensed under the GPL 3.0.

**WIP WARNING:** OmniC is still 'unreleased software', a work in
progress. The API is subject to rapid change. I intend to release the
first stable version before the end of this year (2017).

Installation
============

Installing directly on your host system
---------------------------------------

**NOTE: Only Python 3.5+ is supported.**

The first step is simply installing the Python package:

::

    pip3 install omnic

You likely will want to install a few more python dependencies

::

    pip3 install sanic pillow jinja2 uvloop

Depending on your needs, you will probably want to install a variety of
other system-level package conversion programs. This might include:

-  ``unoconv`` - for converting many document formats - Debian package:
   ``sudo apt-get install unoconv``
-  ``imagemagick`` - for raster image conversion and manipulation -
   Debian package: ``sudo apt-get install imagemagick``
-  ``inkscape`` - for vector conversion and manipulation - Debian
   package: ``sudo apt-get install inkscape``

Additionally, converters specific to certain domains might be useful:

-  ``meshlab`` - for converting between 3D model types - Debian package:
   ``sudo apt-get install meshlab``
-  ``jsc3d`` - for rendering 3D models in software - node package:
   ``npm install -g jsc3d``
-  ``obabel`` - for converting between chemical molecule filetypes -
   Debian package: ``sudo apt-get install obabel``

TODO: Using Docker
------------------

The ideal situation would be to build a (bulky) docker image to support
ALL built-in converters, a ready-to-use kitchen-sink of file conversion.
This has not yet been done.

Usage
=====

There are 3 principle ways to use OmniC

1. Commandline conversion and thumbnailing system
-------------------------------------------------

While OmniConverter was written for the web, the server components are
optional. Thus it doubles as a handy "swiss-army knife" of file conversion
and thumbnail generation.

-  Example: Create thumbs of ``.doc`` and ``.pdf`` files with:
   ``omnic convert --type thumb.jpg:200x200 input.doc input2.pdf``

2. Ready-to-use conversion and thumbnailing web-server
------------------------------------------------------

The most common usage of OmniC is as a microservice, supplying
on-the-fly file format converter and preview or thumb generator,

-  Running a server is as simple as ``omnic runserver``

-  Create a new ``settings.py`` file to customize (use ``OMNIC_SETTINGS``
   to point to it)

3. General purpose media conversion web-framework
-------------------------------------------------

OmniC is written in a very modular format, with a structure inspired
partially by Django. This allows you to tailor-make your own converters,
using it as a library, without forking. You can easily swap out any
part, also.

::

    omnic startproject project_name

Write your own converters and include them in ``settings.py``. No full
documentation or scaffolding is available for this yet: Take a look at the
``omnic.builtin`` for examples on writing your own converters or services.

Launching the admin interface
=============================

OmniC comes bundled with a read-only admin interface. It's main purpose
is a sort of configuration sanity check, and queue monitoring, but it
also serves as a great demo. Once installed, get the omnic server
running:

::

    omnic runserver

Now point your browser at ``http://localhost:8080/admin/`` for the admin
interface.

From here you can paste in an URL to a resource, that OmniC will attempt
to display as a thumbnail. In this example an OBJ file (3D model format)
of a trumpet was pasted in, and a 200x200 thumbnail was generated:

.. figure:: docs/images/admin_conversion_view.jpg
   :alt: Admin interface screenshot

   Admin interface screenshot

To the right of the thumbnail it has an HTML snippet (the source-code of
the thumbnail to the left), and a button that will take you to the
conversion graph for that type:

.. figure:: docs/images/admin_graph_view.jpg
   :alt: Admin graph screenshot

   Admin graph screenshot

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

Misc
====

Test routes
-----------

If you want to test it without the admin interface, take a look at the
following URLs.

To test it, try visiting something like:

-  http://localhost:8080/media/thumb.png:200x200/?url=unsplash.it/450/450

The first time you visit it it will just be a single placeholder pixel.
Subsequent times it should be 200x200 thumbnail

You might also be able to run this, if you have ``unoconv`` and
ImageMagick (providing the ``convert`` command) installed:

-  http://localhost:8080/media/thumb.jpg:200x200/?url=imr.sandia.gov/imrtemplate.doc

This will convert the ``.doc`` into a PDF, then into a JPG thumbnail

If you have ``jsc3d`` installed (a Node JavaScript based 3D model
renderer), then the following should render a delightful trumpet:

-  http://localhost:8080/media/thumb.jpg:200x200/?url=people.sc.fsu.edu/~jburkardt/data/obj/trumpet.obj

Molecular visualization:

-  http://localhost:8080/media/thumb.jpg:200x200/?url=wiki.jmol.org/images/c/ca/Caffeine.mol

The built-in converters interface with a variety of system binaries in
order to provide rendering and conversion of many document, image, mesh.
Adding new converters and rasterizers is simple, with relatively minimal
code!

Production
----------

OmniC is not yet production ready, although you are welcome to try.

The intended use is running as a microservice as part of a larger server
infrastructure. This is to supplement or fully replace traditional
work-queue based systems, such as using Celery. In a reasonable server
topology, many ``omnic`` servers would sit behind a sticky load balancer
(such as nginx), configured to "stick" based on the url GET component.
In such a arrangement each omnic server would not need to be aware of
its neighbors. The load balancer and/or an upstream proxy should also be
configured to cache aggressively, to avoid Python serving static files
(same philosophy to the ``whitenoise`` package).

The rationale for using omnic over a work-queue system:

1. It is stateless with the exception of (disk-based) caching, and,
   technically, (in-memory) queueing although both are non-critical, as
   either getting cleared results in only a slower service, not a
   non-functioning service.

2. The load-balancer topology proposed above would eliminate the need of
   servers to be away of siblings. This results in a much easier to
   understand topology, and a very light-weight dev environment

3. Processing, network, and disk space are coupled, which would make it
   very cheap to run on AWS or DO (I intend to make the $5 nodes
   sufficient).

Misc
~~~~

-  Used Nekroze' cookiecutter to start this package: https://github.com/Nekroze/cookiecutter-pypackage

Documentation
-------------

TODO: Add full docs at http://omnic.rtfd.org."""

