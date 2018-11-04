.. figure:: docs/images/logo_medium.png
   :alt: OmniC Logo

Omni Converter
==============

|Join the chat at https://gitter.im/omniconverter/Lobby| |Build Status| |PyPI| |PyPI version|

Mostly stateless microservice for generating on-the-fly thumbs and previews of
a wide variety of file types. Comes battery-included, but designed like a
framework to be extended into any arbitrary conversion pipelines.

Omni Converter (which can be shortened to OmniC or ``omnic``) is free software,
licensed under the GPL 3.0.

- **WIP WARNING:** OmniC is still 'unreleased software', a work in progress.
  The API is subject to rapid change. I intend to release the first stable
  version before the end of this year (2017).

Docker
======

This repo provides a (very bulky) Dockerfile for working with OmniC. The
advantage is you don't have to worry about tracking down system dependencies to
take advantage of the built-in conversion graph.

1. Install and configure docker on your machine

2. Build the image: ``docker build .``

3. Run the image: ``docker run -it -p 127.0.0.1:8080:8080 <IMAGE HASH>``

4. Go to http://127.0.0.1:8080/admin/ to see the admin interface demo

Run the test suite: ``docker run -it <IMAGE HASH> py.test``

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


Documentation
-------------

.. |Join the chat at https://gitter.im/omniconverter/Lobby| image:: https://badges.gitter.im/omniconverter/Lobby.svg
   :target: https://gitter.im/omniconverter/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
.. |Build Status| image:: https://travis-ci.org/michaelpb/omnic.svg?branch=master
   :target: https://travis-ci.org/michaelpb/omnic
.. |Documentation| image:: https://readthedocs.org/projects/omnic/badge/?version=latest
   :target: http://omnic.readthedocs.io/en/latest/?badge=latest
.. |PyPI| image:: https://img.shields.io/pypi/v/omnic.svg
   :target: https://pypi.python.org/pypi/omnic/
.. |PyPI version| image:: https://img.shields.io/pypi/pyversions/omnic.svg
   :target: https://pypi.python.org/pypi/omnic/

What is OmniC?
==============

OmniC can do a lot of things. Most likely you will want it for making
visualizations and thumbnails without (any other) backend code. It is inspired
in part by `White Noise`_ -- notably, reducing complexity by serving media with
Python.

.. _`White Noise`: http://whitenoise.evans.io/en/stable/#infrequently-asked-questions


On-the-fly media processing
---------------------------

- OmniC is a web server that listens to requests like
  ``/media/thumb.png:200x200/?url=mysite.com/myimage.jpg``, and then downloads
  the `myimage.jpg` file, generates a 200x200 thumbnail of it, and responds
  with that thumbnail.

- It can also do filetype conversions like
  ``/media/PDF/?url=mysite.com/mydoc.doc`` for a PDF representation of a
  ``.doc`` file.

- OmniC doesn't reinvent any wheels, instead it consists of **a framework to
  stitch together existing CLI converters** and expose them all as a
  microservice

Extensible conversion graph
---------------------------

- Central to OmniC is the "Conversion Graph": **you give the URL to a file, and
  the desired type, and it finds the shortest path**  even if it takes multiple
  conversions

- OmniC comes "batteries included", and comes with converters for 3D files,
  documents, images, and more -- but if that's not enough, **it only takes a
  few lines to add your own converter**

Caching
-------

- Since conversion is slow, **every step is cached** so it is only done once,
  and in production it should sit behind an upstream cache or CDN

- OmniC thus potentially can replace worker/queue systems with a much simpler
  solution, **making dev environments far simpler** while resembling
  production, and **potentially reducing worker/queue scaling problems to load
  balancing problems**

JavaScript framework
--------------------
- OmniC comes with some JS to smooth over the experience: For uncached media,
  it will initially serve a placeholder to avoid timeouts, but with the
  included JS snippet it will reload the relevant assets when the conversion is
  finished

- OmniC also provides an **optional JavaScript viewer system**, hooked right
  into its conversion system: For example, a Word document might initially show
  as a JPG thumbnail, then on click show a PDF-based viewer in a modal

Replacing the build step
------------------------
- OmniC's concept of conversion is extremely broad and versatile: For example,
  it can build minified JS bundles from ES6 sources

- Ideally, OmniC could replace most of the build-step during production
  deployments, making launches simply deploying new code to app servers, and
  everything else gets done as-needed on the first request (such as by a tester
  on staging)

