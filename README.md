PyAFIP
======

PyAFIP is a basic python library for accesing some of AFIP's web services.

It is currently work in progress: some services (wsaa and wsfe) are feature
complete. Other services and some improvements in error handling are still
pending.

See the files in `examples/` for examples. These also double as test scripts
(*not* unit tests) to manually test funcionality.

Requirements
------------

Due to dependency incompatibilities, PyAFIP only works with Python 2.7. It has
been properly tested on 2.7.9, but is expected to work on previous versions as
well.. You'll also require:

* [m2crypto](https://github.com/martinpaljak/M2Crypto)
* [lxml](http://lxml.de/)
* [suds](https://fedorahosted.org/suds/)

Copyright (c) 2014-2015, Hugo Osvaldo Barrera <hugo@barrera.io>
