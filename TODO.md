# Next steps

Blocking order:
1. Build better testing infrastructure
2. Fix packaging + docs
3. Make scaffolding
4. Write containers for a few builtin setting-sets, such as 'kitchen sink',
'image', and 'empty', allowing to lock down specs
5. Build CLI-level tests that include mini-scaffold test apps for full e2e
(rendering all tests in tests/ directory merely unit and integration tests)
6. Create "zoo" repo of specimen and include full e2e tests on all zoo specimen

## Top priority
- [ ] Get viewer demo running
    - [X] Add `just_checking` media API
    - [X] Create new viewer format that is just a bare npm repo with
      `__init__.py` (later could mix in Python metadata)
    - [ ] Improve dev environ for JS
        - [X] `omnic clearcache http://foreign/resource/ --type=min.js`
            - [X] Without type it will clear entire cache
        - [X] `omnic precache http://foreign/resource/ --type=min.js`
            - [X] Optional `--force` which will do `clearcache` first
        - [X] `omnic precache-named viewers --type=min.js` - same as
          above, except just viewers
            - [ ] Get fully compiling
        - [ ] `make js-watch`
            - `find *.js | entr omnic precache-builtin viewers --type=min.js`
    - [ ] Create omnic base viewer
    - [ ] Add testing utilities in JS, using node (jasmine? or something more
      trendy?)
    - [ ] Add in the following viewers:
        - [ ] Image (lightbox style pop-up, see whats most popular)
        - [ ] 3D with JSC3D
    - [ ] Possibly add in web-worker hook system to base viewer (?) so I can
      add PDF.js to the demo
        - [ ] Build 1 JS package, but detect if in web worker or not, and
          execute different code path for each
    - [ ] If viewer infrastructure is as robust as I intend, add a bunch more
      viewers:
        - [ ] SVG pan
        - [ ] Video player
        - [ ] Audio player
        - [ ] Markdown
        - [ ] Syntax highlighting
        - [ ] Various data viz stuff (CSV -> graph)
        - [ ] Molecule (2D)
        - [ ] Molecule (3D)
    - [ ] Ambitious viewer ideas:
        - [ ] One viewer be draggable maps. Render tiles from BytesResource service
        - [ ] Git tree viewer -- essentially embeddable github -- with ALL THE
          OTHER viewer types hooked in
            - [ ] This would make a stupendous demo on the omnic site
            - [ ] Types with multiple viewers (e.g. CSV) can be swapped with a
              tab interface

- Git notes
    - Adding git to conversion graph:
        - Generalize concept of conversion to include ForeignResource ->
          LocalResource
        - Add 'GitForeignResource' that can be converted to folder, or a file
          within that folder
        - Conversion then gets git foreign resource at a particular hash and
          translates that to a folder, which in turn can transform into a
          particular file (caching correctly each step)
    - Git viewer
        - Do the 'Doc Write' strategy I came up to block page on HTML render

- [ ] Switch to `MULTICONVERT` and async enqueues
    - [X] Create `MULTICONVERT` task type
    - [ ] Remove sync `FUNC` task type (requires lots of test changes)
    - [ ] Remove all synchronous enqueues (requires lots of test changes)

- [ ] Switch to `MULTICONVERT` and async enqueues

## Misc

- [ ] BUG: Fix running unoconv within venv
    - [ ] Check if in virtualenv and ensure system Python is used when doing
      subprocess calls

- [ ] QoL conversion grid improvements
    - [X] ~Think more about how to make extension "supersede" mimetype
      in a reliable way~ The detector system generally takes care of this
    - [X] Add "configure" check to base Converter, which should ensure correct
      Python and system packages installed for the converter to be functoinal
    - [ ] Allow conversions to self
    - [X] Allow full conversion paths in settings, which are picked first if
      available (useful for locking down)
    - [X] Allow 'conversion profile' system, which ranges from aliases, to
      partial conversion path

    - [ ] Locking + sanity check process:
        - [ ] 1. Before, optionally (based on conf) do sanity Detector check
        - [ ] 2. After, optionally (based on conf) do sanity Detector check
        - [ ] 3. After, (required) make output all exclusively readonly,
          recursively in the case of a directory
        - [ ] 4. `Resource` base class should treat writable caches as
          non-existent, thus making "in progress" files unusable to front-end
          services. This step is essential for data integrity.
        - [ ] Obsolete Detector Converter types, I believe

    - [ ] For JS, should have full input graph, e.g. can uglify plain JS files,
      but rely on "preferred paths" to ensure that it gets es5ified first (can
      configure in default settings this way)

    - [ ] It's becoming increasingly clear I need to build a constant-based
      TypeString hierarchy, such that a bundle.js or es5.js is a type of JS
      file, and thus gets proper mimetypes, etc, while remaining more specific

- [ ] AsyncIO improvements
    - [ ] Replace all file system calls with aiofiles
    - [ ] Replace all spawn system calls with asyncio equivalent


# Build out builtin

# CLI and packaging
- [ ] Document the three uses:
    - CLI and library - Include in other projects (e.g. Django, Celery) as a
      useful conversion utility
    - Ready-to-go server - Provide docker container to spin up behind nginx,
      using env variables to configure, only providing a settings.py file if
      necessary
    - Web media conversion framework - In the manner of Django, Flask, etc have
      a cookiecutter example of setting up an new project, and hooking in your
      own Services and Converters

# Future

## JS viewer system
-[ ] First API call looks for all `img[omnic-viewer]` and
  `img[omnic-thumb]` tags and sends 1 AJAX call to check if they are all
  loaded.
    - [ ] If not, it will add a spinner to all thumbnails of them, and
      try again in X seconds (V2: could keep running average of every
      conversion path, and try again in `avg * 1.5` or something)
    - [ ] If loaded, it will check if omnic-viewer, then add a
      hoverable (>) button in the center, and an onclick event which
      will activate the appropriate viewer
    - [X] If possible / cheap computationally, avoid API calls by
      checking if the image is a 1x1 placeholder image (?)
- [X] New Viewer system: Each type can have a Viewer, that serves up JS
  that mounts a viewer on a particular element (given a URL). E.g. the
  STL, OBJ etc viewer, when clicked on, will enable JSC3D.
    - [X] All registered viewers get served up on page load in one
      minified JS bundle
    - [X] They only get "activated" as needed
- [X] Embed in page components
    - `<img src="...omnic/media/thumb.jpg..." omnic-viewer="PDF" />`
    - The JS looks for all tags with `[omnic-viewer]` and adds a click
      event that will embed the correct type of viewer for that element

## Queueing
- [X] Allow attachment of any arbitrary traditional task-queueing backend
- [ ] Allow swapping out asyncio's gimmick-y queuing for a custom-made
  Redis-based async queue (should be easy) e.g. using: `aioredis` package

## Rendering services
- [X] ByteResource - A type of resource where the contents is a short
  string, already in memory

- [ ] /render/ Service - A service that takes in ByteResources and outputs
  other things.
    - Example: `/render/osm-geo:79.1239,32.231345,12/thumb.png:200x300/` --- This
      would render Open Street Map into an image, and then use the PNG -> Thumb
      converter to resize to the right size
    - Example: `/render/text3d:"Hello World!"/webm:200x300/` --- This would
      generate Hello World text as 3D shape (obj file), then use the OBJ ->
      WEBM to make a rotating image


## Bundling service
- NOTE: Even with the manifest.json media type, this  still be useful,
  for more convenient manifest format...?
- [ ] zip, tar.gz, tar.bz2, 7z - all bundle formats
- [ ] A more convenient manifest format that allows conversion, maybe a bundle
  service to go along with it: /bundle/ Service - A service that takes in an
  URL to a json manifest file, which contains an array of files and conversion
  destinations to be processed.
    - Example: [
        {
            "url": "http://host.com/file.png",
            "path": "media/image/file.png",
            "type": "JPG"
        },
        ...
    ]

## WebSocket RPC service
- [ ] /ws/ Service - Exposes all other services via a websocket RPC-like
  interface. Useful for creating more involved progress-bar UIs etc and
  pre-caching longer-running processes
    - Still would have no trust, simply exposing the public HTTP interface in
      another way, for more involved front-end applications
    - Example:
        - `< "media", {url: "foo.com/bar.pdf", typestring="thumb.png"}`
        - `> "downloaded", {url: "foo.com/bar.pdf"}`
        - `> "converting", {url: "foo.com/bar.pdf", type="PNG"}`
        - `> "converting", {url: "foo.com/bar.pdf", type="thumb.png"}`
        - `> "ready", {url: "foo.com/bar.pdf"}`
        - `< "bundle", {url: "foo.com/bar.json"}`
        - `> "in-progress", {url: "foo.com/bar.json"}`
        - `> "downloaded", {url: "foo.com/bar.json"}`
        - `> "downloaded", {url: "foo.com/bar.json"}`

## JS converter
- [X] Minifier and JSX / TypeScript compiler
- [X] Possibly a service dedicated to this, or just use /bundle/ wit ha
  different target type ('js')
- [ ] Support more JS build systems
    - [ ] Webpack based bundling + compilation
        -  TODO For "full webpack packages", that is, ones with custom config
           scripts that may require executing untrusted code.  Needs to somehow
           guess where files will end up. This path SHOULD NOT be allowed in
           normal confs.
    - [ ] Babelrc based compilation

## Packaging build server Converters
- [ ] Convert "tar.gz" -> rpm, deb, appimage, flatpak etc
- [ ] Convert "python-project.git" -> rpm, deb, appimage, flatpak etc
- [ ] Convert "electron-project.git" -> rpm, deb, appimage, flatpak etc

## Mesh
- Blender integration
- [X] Possibly create a JSC3D node module port / fork that uses `node-canvas`,
  and expose a CLI that can render (via software) STL models and such
- [ ] DXF

## CI + Code badges
- "CI as a microservice"
- Code badge generation - allow another service that is 'ci', which can be
  given a (whitelisted) git repo. It then downloads that git repo and attempts
  to run something (e.g. with docker). Any remaining artifacts then enter the
  "media conversion graph".
- Artifacts could include code coverage graphs, badges, etc
- They could also include built websites, then conversion graph could include
  launch
- Just in time deploy: Have serving HTML (e.g. not data) actually trigger build
  of entire (e.g. static) site from a repo (HTML served before ready just shows
  spinner and refreshes page when ready)
- Thus, omnic becomes "just in time deployment"
- Obvs in real life, this would be triggered with a hook

# Production caching control improvements

## Commands

- [X] 'precache' command - triggers conversion / whatever, and blocks until
  finished. Useful for adding as a build step.
- [X] 'clearcache' command - delete a single foreign resource from cache,
  removing all generated media from that foreign resource.
    - [ ] Also support date-range.
- [ ] 'omnic-clear-cache-cascade' application - special separate (?)
  application that would hook into any upstream proxies AND all siblings, fully
  wiping the cache for a certain foreign resource

## Resource system improvements

- [ ] 'mutable' concept - some foreign URLs might be mutable. All media
generated from them should have much more cautious client-side cache headers.
- [ ] Time-based grouper: In addition to MD5 structure, have
    `/var/tmp/omnic/date-cache/2017/08/01/ae08/`. This will allow cron to
    aggressively purge older cache, e.g. only maintain a couple days in prod.
    This is good because IRL it won't be serving media anyway, the cache is
    only good for conversion.

## Cron

- [ ] CronWorker system, added to the main loop, that asyncio sleeps every 5
  minutes and checks a cron queue
- [ ] Cron queue is for cache clean-up tasks, queue monitoring (could send
  alerts somehow if queues get out of hand), etc


# QoL improvements

- [ ] TypeStringMatcher
    - Can match based on mimetype categories, or custom properties
    - Usable on Placeholders
    - Not usable on Converters, presently, since it would impair creation of
      ConverterGraph

- [ ] Built-in lists of common formats to be used, along with common
  placeholder pixels

# Code quality improvements

- [ ] Turn on `_FORCE_PREVENT_LOGGING_DISABLE` and clean up warnings in tests
  (since some indicate some messy stuff being left behind during the tests)

- [ ] Refactor worker manager, worker, and task system (right now has a lot of
  repetitive code)
    - [ ] Make tasks be definable independent of ENUM / custom methods

# Performance and stability improvements

- [X] Performance hack: Have a "sticky queue" system where resources go into
  several worker queues based on hash on URI
    - More importantly this would allow processing multiple resources at once,
      and assumedly max out CPU better e.g. if waiting on slow net IO, could be
      using that CPU for local conversion
    - [ ] Long term solution: Allow task ordering in work queue system
        - This would allow download + all conversions be queued w.r.t. each other

# Decided against

- [ ] Checked in cached built version of viewer
    - [ ] `CACHE_ALIAS = {'viewers.min.js': {'/path/to/checkout/...'}}`
- Pool should probably be configured, and always run with `runserver`
- [ ] Redis-only commands:
    - `omnic runworker` -- runs a worker-only process
    - `omnic runserverworker` -- runs a process that is both server AND worker
    - `omnic runmulti --worker=1 --server=1 --serverworker=2` -- runs X
      processes of the given types
- [ ] @localserver context manager (?)
    - [ ] Allows "mini local server" that has can make fake queries via
        custom routing
    - [ ] Something like: await f.client.get('/media/?qs=abc')
    - [ ] General merger of client convert code (should actually spin up
        workers) + server routes

