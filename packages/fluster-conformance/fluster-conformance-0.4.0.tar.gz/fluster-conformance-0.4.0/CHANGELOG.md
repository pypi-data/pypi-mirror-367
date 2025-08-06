# CHANGELOG


## v0.4.0-rc.1 (2025-08-05)

### Bug Fixes

- Adapt code related to handle_terms parameter
  ([`efe796b`](https://github.com/fluendo/fluster/commit/efe796bb93f8b9c1b601fbee39f3573260ae1568))

- Add provider "Fluendo" to FluendoMPEG4VideoDecoder
  ([`1f4b33d`](https://github.com/fluendo/fluster/commit/1f4b33d47b6ab9d1bd0c07b1319af11563edc4c7))

- Fix freeze bug when generating test suite with limited available RAM
  ([`385121b`](https://github.com/fluendo/fluster/commit/385121b7dbd08a5d5cd170d5441a5cb6d4dc6f7c))

- Prevent test suite execution when missing resources
  ([`24e747c`](https://github.com/fluendo/fluster/commit/24e747ceb64b9a0d0fd3bf715be85b872369c6da))

resolves #232

- Remove handle_terms from MPEG4 video test suites
  ([`784c090`](https://github.com/fluendo/fluster/commit/784c090b9d0a88fb170aaa33ced84562f4336e3c))

- Vkvs use enablePostProcessFilter
  ([`e5ba4ca`](https://github.com/fluendo/fluster/commit/e5ba4ca67df299091f4862f949b599b29b3e6a6c))

Use enablePostProcessFilter by default to support hardware with different queue for decode and
  transfer such as mesa drivers.

See https://github.com/KhronosGroup/Vulkan-Video-Samples/issues/57

### Build System

- Adapt gen_mpeg4_video.py for advance simple profile
  ([`ada94c2`](https://github.com/fluendo/fluster/commit/ada94c22f4882e55608d8fd1ac24af6012737d50))

- adapt extract method in utils.py - add profiles to this test suite

- Adapt gen_mpeg4_video.py for simple scalable profile
  ([`aac0910`](https://github.com/fluendo/fluster/commit/aac0910391f126a9cb656a2080fc076790f08cca))

- add exceptions in profiles

- Adapt gen_mpeg4_video.py for simple studio profile
  ([`7689f54`](https://github.com/fluendo/fluster/commit/7689f5414939d3ee12868f55c684afc2946db999))

- adapt the download method in utils.py with chunk to download large files - add exceptions in
  profiles

- Add "flumpeg4vdec" decoder to gstreamer.py
  ([`5cae5ee`](https://github.com/fluendo/fluster/commit/5cae5eef8827eb1740f1f3b4ab222b4f2638d8f0))

- Add GStreamer Libav "avdec_mpeg4" decoder to gstreamer.py
  ([`51c29eb`](https://github.com/fluendo/fluster/commit/51c29eb29f62f18b5a07a11921e31de74adf35ea))

- Add iso_mpeg4_video.py to pass tests with reference decoder (only binary)
  ([`9d73e4d`](https://github.com/fluendo/fluster/commit/9d73e4d4c7de302b2a1f99ba9733922ab371705e))

- compiled in a private repo (gcc 13.0.1) - adapt to method pixel - adapt test.py to both decoders
  because mpeg4v ref_dec generate output files with .yuv extension directly

- Add MPEG4 video generator script
  ([`0f5d756`](https://github.com/fluendo/fluster/commit/0f5d7568b2625a45b4bbd84cb80f0570f6b7e2a5))

- needs to fix "I accept" to download some test vector automatically - add new "handle_terms"
  parameter to manage previous point - add SIMPLE_PROFILE = "Simple Profile" in codec.py

### Chores

- Add FFMpeg mpeg4 video decoder
  ([`ba8205f`](https://github.com/fluendo/fluster/commit/ba8205fcd4f212da495c587df1fa4b0ee32cf957))

- Add output format exceptions for some H.264 test vectors
  ([`8ca9a3e`](https://github.com/fluendo/fluster/commit/8ca9a3e58e321260c311198ac8b22e44d3110829))

- Add profile information to H.264 test suite generator
  ([`8dfd54c`](https://github.com/fluendo/fluster/commit/8dfd54c0f9033ca12ada4ce3dfae94e049763025))

- Add profile information to H.265 test suite generator
  ([`4132ddb`](https://github.com/fluendo/fluster/commit/4132ddb50daec91dc415d2c2fbd737b45d43bf03))

- Add profiles for H.265 test vectors
  ([`823e404`](https://github.com/fluendo/fluster/commit/823e404a653d9ef7a85e4bd1daf4643255f42be3))

- Update H.264 test suites with profile information
  ([`7ac1722`](https://github.com/fluendo/fluster/commit/7ac1722578926513982a615b47baca44d74c8feb))

- modify JVT-AVC_V1, JVT-FR-EXT, JVT-Professional_profiles test suites

- Update H.265 test suites with profile information
  ([`b110c97`](https://github.com/fluendo/fluster/commit/b110c97510f8b6303d7e30bff213de63fcea2bc5))

- modify JCT-VC-HEVC_V1 test suite

### Documentation

- Add MPEG4_VIDEO info to README.md
  ([`83b2a13`](https://github.com/fluendo/fluster/commit/83b2a1348aac93f5bb66121f58acd5577089d817))

- Changelog.md and pyproject.toml updated manually to new 0.4.0 release
  ([`736fd56`](https://github.com/fluendo/fluster/commit/736fd565518fcff1782716967a403a1c8050c54b))

- Update documentation for a new release 0.4.0
  ([`bae0b64`](https://github.com/fluendo/fluster/commit/bae0b643af90395aaf51d245d688ff46c7fa4e1f))

- add pixel comparison method info to description of README.md - add MPEG4 Video test suites to
  pyproject.toml - add other MPEG4_VIDEO info to README.md

- Update README.md with latest test suites and minor fixes
  ([`4eb1bb1`](https://github.com/fluendo/fluster/commit/4eb1bb18863b1f02c3d199a6bd4681bf6a4e9ab2))

### Features

- Add gst vulkan AV1 decoder
  ([`cda75c7`](https://github.com/fluendo/fluster/commit/cda75c7b31cae54ea975cf1e73a855adfa041ede))

Add AV1 to the list of supported decoders by GStreamer.

- Add mpeg4 video test suite for advanced simple profile
  ([`550bb21`](https://github.com/fluendo/fluster/commit/550bb2100b3dc06dc344f46b0249097d969ae01a))

- Add mpeg4 video test suite for simple profile
  ([`ec8848a`](https://github.com/fluendo/fluster/commit/ec8848a3fff83d7f4764640a7e02c3ff96f7ad47))

- "result": "" until to know if reference decoder is (FFMpeg mpeg4)

- Add mpeg4 video test suite for simple scalable profile
  ([`48262cf`](https://github.com/fluendo/fluster/commit/48262cf659a4ce68e95f2497b6c546189fbf7297))

- Add mpeg4 video test suite for simple studio profile
  ([`1fdbfac`](https://github.com/fluendo/fluster/commit/1fdbfac71ab45249e1faf4f3af8f1291e8a8e3cf))

- Add per profile test results to markdown summary report
  ([`1faaad4`](https://github.com/fluendo/fluster/commit/1faaad41895cdaf082cfdca356a3efa3aa7b6ab3))

- if profile information is available, passed over total number of vectors per suite will be printed
  in markdown summary report

- Add support for test vector profile as optional parameter
  ([`f807d7d`](https://github.com/fluendo/fluster/commit/f807d7d6ad8c7abcaa4e72a89bd4a1371475486b))

- create profile enumerator class for H.264 profiles - modify test vector class structure

- Add vp9 decoder for VKVS
  ([`e932bfd`](https://github.com/fluendo/fluster/commit/e932bfdf2409dcd7ec02cc789fdedde387152616))

- Add vulkan vp9 decoder for GStreamer
  ([`390e289`](https://github.com/fluendo/fluster/commit/390e28946aea4aa2ca1b1ba73665554b3b8c2e34))

- Support wildcard in list of tests
  ([`33566ab`](https://github.com/fluendo/fluster/commit/33566abd09641ad3d5e096d75cef86d3b769d0c7))

To select a set of test vectors with a pattern, use of fnmatch on the list of test vectors.

It allows to get a sub list of test vectors, ie:

./fluster.py run -s -d GStreamer-VP9-VA-Gst1.0 -tv vp90-2-12* vp90-2-11*

vp90-2-11-size-351x287.webm|✔️| |vp90-2-11-size-351x288.webm|✔️| |vp90-2-11-size-352x287.webm|✔️|
  |vp90-2-12-droppable_1.ivf|✔️| |vp90-2-12-droppable_2.ivf|✔️| |vp90-2-12-droppable_3.ivf|✔️|

### Testing

- Changelog.md updated automatically
  ([`4b2cf86`](https://github.com/fluendo/fluster/commit/4b2cf86d8c75724cc94778f8f30d80b07ef8c58f))


## v0.3.0 (2025-04-17)

### Bug Fixes

- Add new line to the json file
  ([`3f33ebc`](https://github.com/fluendo/fluster/commit/3f33ebc1b00b7b7fd625f060e44f6e5ee6fe29fb))

- Create mpeg4 reference decoder for error resilient test vectors
  ([`973657d`](https://github.com/fluendo/fluster/commit/973657dcda0348aaefb9bd3388f9fef5174a5e62))

- Split mpeg4 aac test suite into error and non error resilient test vectors
  ([`16f3c08`](https://github.com/fluendo/fluster/commit/16f3c083b1a5d373224f25f0b427303ad28ce352))

- Update MPEG4_AAC-MP4-ER.json with new md5sum generated and update iso_mpeg4_aac-er.py for generate
  interleave multichannel
  ([`2d0e3b5`](https://github.com/fluendo/fluster/commit/2d0e3b5f7d19dee2b24ace692d2306b982943b9c))

- Update MPEG4_AAC-MP4.json with new md5sum generated and update iso_mpeg4_aac.py for generate
  interleave multichannel
  ([`37c7a6c`](https://github.com/fluendo/fluster/commit/37c7a6c6cf578bea4aa51ee9a9cc0575313306eb))

### Build System

- Add mpeg2v test suites to pyproject.toml
  ([`8f6ee47`](https://github.com/fluendo/fluster/commit/8f6ee476e112d159c6eda67ad96fb53ad319e14b))

- Add mpeg4 aac mp4 error test suite for aac decoder
  ([`ef193f0`](https://github.com/fluendo/fluster/commit/ef193f0f63a0af84a181d5b5dbc049af2c168e1f))

- Add reference decoder mpeg2dec installation to Makefile.
  ([`116fbd1`](https://github.com/fluendo/fluster/commit/116fbd188b84b82e8db258b04b621ea30927cba7))

- Adds the helper script to generate the test suites
  ([`4ca706f`](https://github.com/fluendo/fluster/commit/4ca706fa2e3667068145a378db199ed22fd363e2))

- Change Pypi version to deploy in a new 0.3.0 release from master
  ([`15c9b2b`](https://github.com/fluendo/fluster/commit/15c9b2be547e67f8a6540a678172c3ad17c72276))

- Remove depedencies from pyproject.toml
  ([`55885ba`](https://github.com/fluendo/fluster/commit/55885ba1a7e5050099a2ad08af1d93579beda234))

- removed optional-dependencies from project group. this group is meant for runtime deps of specific
  sw features

### Chores

- Add some gstreamer mpeg2video decoders
  ([`f815efa`](https://github.com/fluendo/fluster/commit/f815efa33388cdd55e35ed35d0d19ca022cb43fc))

- add gstreamer mpeg2dec (libmpeg2) video decoder - add gstreamer avdec_mpeg2video (libav) video
  decoder

- Omit VP8, VP9 and AV1 Makefile check tests when MacOS
  ([`bb09a89`](https://github.com/fluendo/fluster/commit/bb09a892616db35c7b44d594024655fae584a260))

- libaom-AV1, libvpx-VP8, libvpx-VP9 decoders are not readily available

- Remove mypy and ruff from Makefile
  ([`7aba017`](https://github.com/fluendo/fluster/commit/7aba0178e515303294821acd672e85b9204887ca))

- remove lint, lint-check and format targets from Makefile - clean obsolete variables in Makefile

- Remove ruff and mypy packages from project requirements
  ([`c359361`](https://github.com/fluendo/fluster/commit/c359361b81255ee24089bb90a090ed04c1c6fdf7))

- Rename requirements.txt to requirements-dev.txt
  ([`b560302`](https://github.com/fluendo/fluster/commit/b560302244a970f1b01f242631d09c9cbd96618f))

### Continuous Integration

- Add mypy as pre-commit hook in .pre-commit-config.yaml
  ([`358a8e3`](https://github.com/fluendo/fluster/commit/358a8e327ddce60a409fe538d395197ebe7179d2))

- Change ruff pre-commit hook to automated fix mode
  ([`3138c41`](https://github.com/fluendo/fluster/commit/3138c41202ad0a8ea0e66b571257db8263af201b))

- Replace ubuntu 20.04 with 22.04 in GHA runners due to deprecation
  ([`5b7b8ba`](https://github.com/fluendo/fluster/commit/5b7b8ba60390f77c50fe84c5f9c61628c3d523c9))

### Documentation

- Add "ISO-MPEG2-VIDEO: ISO MPEG2 Video reference" decoder to README.md
  ([`2f2bb22`](https://github.com/fluendo/fluster/commit/2f2bb2243cbff78f08bf979ad1e72bbecde1dd76))

- Add mpeg2 video decoders information to README.md
  ([`a3c49a4`](https://github.com/fluendo/fluster/commit/a3c49a45b5660843ca2138b2194231de24b8910a))

- Add test suite for mpeg4 aac mp4 error test vectors
  ([`573bb64`](https://github.com/fluendo/fluster/commit/573bb649ff4f696c4394240ab33e0fb3a3734c38))

- Update README.md
  ([`b640fe5`](https://github.com/fluendo/fluster/commit/b640fe52d807b2ca0224dd60912732e532f24060))

### Features

- Add a pixel comparison method for codecs that don’t generate identical outputs
  ([`acee87a`](https://github.com/fluendo/fluster/commit/acee87a08bbb04505dac25b19ed63b32d7793fce))

-Old codecs like MPEG-2 Video do not use a standarized IDCT (MPEG-C Part1) causing mismatches in the
  generated output. -This new method allows creating tests suites that will compare the output pixel
  by pixel with a tolerance range

- Add ISO IEC 13818-4 MPEG2 test suites
  ([`b01bfe0`](https://github.com/fluendo/fluster/commit/b01bfe0c6efd5f5f70686a7df4e03fcd3adca845))

- Add vah266dec gstreamer decoder
  ([`57a299d`](https://github.com/fluendo/fluster/commit/57a299d5fb25ebe04ec8fd28acb1c8cd0a3145aa))


## v0.2.0 (2025-01-27)

### Bug Fixes

- --check per check (--check is failing in "pre-commit" command)
  ([`8e7f6e8`](https://github.com/fluendo/fluster/commit/8e7f6e879cb58d240529678f5bf53ea1529888bf))

- Parameterise AV1 AOM reference decoder for AV1 argon test suite
  ([`3f20ed8`](https://github.com/fluendo/fluster/commit/3f20ed8dfa41ca74892dadd7a8d4ab2df3122fb5))

- Replace AV1 argon test suite with new ones
  ([`85505b0`](https://github.com/fluendo/fluster/commit/85505b019202fecc18c9a0afdabc662e0627b36b))

- Split AV1 argon test suite by profile, annex, type
  ([`ab3b510`](https://github.com/fluendo/fluster/commit/ab3b510415ed55efe93de585e7141c522189e6b1))

### Build System

- Add "pre-commit install" to install_git_hook.sh, add pre-commit as dependency to requirements.txt,
  remove check-yaml and trailing-whitespace, because we have already ruff check.
  ([`62d3708`](https://github.com/fluendo/fluster/commit/62d37088a6b492c19f4be4d5284a1951328a0ef3))

- Add --verbose option to conventional-pre-commit hook.
  ([`6b4c9cb`](https://github.com/fluendo/fluster/commit/6b4c9cb5875ca8ad2e800abe63b63f0244a27a46))

- Add ruff pre-commit hooks for linting and formatting
  ([`3aa9e87`](https://github.com/fluendo/fluster/commit/3aa9e87dff6eeeb91e74edc859f17302a6615fcd))

- Downgrade pip-commit version to 2.21.0
  ([`2aa8cc8`](https://github.com/fluendo/fluster/commit/2aa8cc8ebb7c53bc395d1d1c14eb17292528ccde))

- Remove "format-check:" usages from Makefile
  ([`b8add4a`](https://github.com/fluendo/fluster/commit/b8add4a05427722bd50c46b293e3f4263bb4f4b0))

- Remove ruff format-check of Makefile, already validated with pre-commit and use "--check" instead
  "check" as arg.
  ([`f923e2e`](https://github.com/fluendo/fluster/commit/f923e2e7d0ab1c716b7e34d054f71c69c04fcc95))

- Replace AV1 argon test suite with new split ones in packaging
  ([`73b5506`](https://github.com/fluendo/fluster/commit/73b5506859085b4eade23ed354fd232f74c24366))

- Set minimum version in pre-commit, ruff and mypy in requirements.txt and yml workflow files.
  Update .pre-commit-config.yaml without fix parameters.
  ([`87d4899`](https://github.com/fluendo/fluster/commit/87d48997e34535ee9f6df8dc3ffc844a5eb19f61))

fix: resolve comments

- Update pyproject.toml manually for publish 0.2.0 release version to pypi.
  ([`50d70e7`](https://github.com/fluendo/fluster/commit/50d70e7e9d11129ef3cd01b421690bccfc34b3fc))

### Chores

- Add spaces in fluster.py help
  ([`c0e47fe`](https://github.com/fluendo/fluster/commit/c0e47fe847608a81bb710ed23953f8f1f2fe7905))

### Code Style

- Update format files to characters per line=120 and increase rc version to test
  ([`cdb0c29`](https://github.com/fluendo/fluster/commit/cdb0c295cfca5cd66dd72dcc9609841f9a38159b))

### Continuous Integration

- Change order and add need file to CI (COMMIT_EDITMSG) and add commit-validation job to
  python-app.yml and release.yml
  ([`544c7c1`](https://github.com/fluendo/fluster/commit/544c7c1015619dd4cff258cf94711bf21be449ff))

- Downgrade OS and python version to minimum supported in min linux job and remove validate commit
  step in release workflow
  ([`9c93d4d`](https://github.com/fluendo/fluster/commit/9c93d4df52d77feca8e5c49a8d91553df632a6ec))

- Fix when "github.base_ref" is from master branch.
  ([`a8e7b2c`](https://github.com/fluendo/fluster/commit/a8e7b2cb58fbaebda37508e49c37998b760bb25d))

- Include "Validate all files" step to "Validate commits" job
  ([`c4999e8`](https://github.com/fluendo/fluster/commit/c4999e8e7b80fb2ee3020181ae8e5b1423a9442a))

- Move "get commit messages" to "validate commit messages" step, improve "pre-commit run" command
  and use "github.base_ref" instead "master"
  ([`2201c6d`](https://github.com/fluendo/fluster/commit/2201c6d387617b6ddae09e28cdcee37c8dd4a359))

- Restrict pre-commit version to 3.0.6 in requirements.txt and CI yml files
  ([`99d44e8`](https://github.com/fluendo/fluster/commit/99d44e8841a9bce8714715d991a83a1a72e38303))

- Validate more than last commit
  ([`9b188cb`](https://github.com/fluendo/fluster/commit/9b188cbfc57bd1078b0ee22539e16811b4eec28e))

### Documentation

- Update changelog manually for 0.2.0 release version
  ([`e930730`](https://github.com/fluendo/fluster/commit/e930730274650c39d54660988369892d8e1f9558))

- Update doc related with "conventional-pre-commit"
  ([`5c45b79`](https://github.com/fluendo/fluster/commit/5c45b79f48c2cb522f0f946b020bb263f7431182))

- Update Makefile comments (pre-commit already covers)
  ([`ac64289`](https://github.com/fluendo/fluster/commit/ac6428954a6ad3b6c9f79cb22830b4b63a0a0e32))

### Features

- Add libaom based GStreamer AV1 decoder
  ([`e06b07d`](https://github.com/fluendo/fluster/commit/e06b07d4e59ce3701e366a2c8451dc94d90076c4))

This is useful to GStreamer project in order to ensure nothing in GStreamer prevents libaom from
  working correctly. This decoder fully passes AV1-TEST-VECTORS, CHROMIUM-8bit-AV1-TEST-VECTORS and
  CHROMIUM-10bit-AV1-TEST-VECTORS. The Argon suites have been ignored for now.

- Automate release process completely taking advantage of semantic commits and already-created in
  GHA and add pre-commit conventional commit messages validation
  ([`b9f003d`](https://github.com/fluendo/fluster/commit/b9f003dc51f6c78308cd3e3f485b1c26c9cace28))


## v0.1.0 (2022-12-20)
