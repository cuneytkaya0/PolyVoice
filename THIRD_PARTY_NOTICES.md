# Third-Party Notices

PolyVoice downloads runtime dependencies and model assets during setup. Downloaded weights, voice packs, Python environments, generated speech, and caches are not part of this source repository. License information below reflects project requirements, installed package metadata, and linked upstream notices checked for this release candidate. It is a summary; retain the complete license files supplied with each package and model.

## Application and model components

| Component | License | Use / attribution |
| --- | --- | --- |
| Kokoro | Apache-2.0 | [hexgrad/kokoro](https://github.com/hexgrad/kokoro); English, Japanese, and Mandarin inference. |
| German-enabled Kokoro fork | Apache-2.0 | [semidark/kokoro](https://github.com/semidark/kokoro), pinned commit `b96fef95e6a746495f92443fac7c688f90fc57fc`. |
| Misaki | Apache-2.0 | [hexgrad/misaki](https://github.com/hexgrad/misaki); language text processing. |
| German-enabled Misaki fork | Apache-2.0 | [semidark/misaki](https://github.com/semidark/misaki), pinned commit `9cda9268309160120fffee216280a9ca83ac4644`. |
| Kikiri German — Martin | Apache-2.0 | [Model card](https://huggingface.co/kikiri-tts/kikiri-german-martin); model and speaker pack downloaded during setup. |
| Kikiri German — Victoria | Apache-2.0 | [Model card](https://huggingface.co/kikiri-tts/kikiri-german-victoria); model and speaker pack downloaded from pinned revisions and SHA-256 checked. |
| Kokoro-82M model and voices | Apache-2.0 | Downloaded from the official [Kokoro model repository](https://huggingface.co/hexgrad/Kokoro-82M); voice assets remain excluded from this source repository. Its model card credits CC BY-licensed training audio from Koniwa (`tnc`, CC BY 3.0) and SIWIS (CC BY 4.0); see the model card's training-data and attribution sections. |

## Runtime dependencies

| Component | License summary | Use / attribution |
| --- | --- | --- |
| `phonemizer-fork` | GPL-3.0-or-later | Fork of [bootphon/phonemizer](https://github.com/bootphon/phonemizer), used by German G2P. |
| eSpeak NG | GPL-3.0 plus separately licensed components | German phonemization backend. Upstream also contains Apache-2.0, BSD-2-Clause, and UCD-licensed files; see [upstream license information](https://github.com/espeak-ng/espeak-ng#license-information). |
| `espeakng-loader` | MIT | Loads the local eSpeak NG library; [source](https://github.com/thewh1teagle/espeakng-loader). |
| `pyopenjtalk-plus` | MIT wrapper; bundled assets have separate terms | Japanese G2P; consult [upstream notices](https://github.com/tsukumijima/pyopenjtalk-plus) for OpenJTalk, HTS voice assets, and marine components. |
| PyTorch | Apache-2.0, Apache-2.0 WITH LLVM-exception, BSD-2-Clause, BSD-3-Clause, BSL-1.0 | CPU tensor and inference runtime; see [pytorch/pytorch](https://github.com/pytorch/pytorch). |
| NumPy | BSD-3-Clause, 0BSD, MIT, Zlib, and CC0-1.0 components | Numerical operations; see [numpy/numpy](https://github.com/numpy/numpy). |
| SoundFile | BSD-3-Clause | WAV encoding/inspection; see [bastibe/python-soundfile](https://github.com/bastibe/python-soundfile). |
| Flask, Werkzeug, Jinja, Click, ItsDangerous, Blinker | BSD-family licenses or upstream package license | Local HTTP interface; see [pallets](https://github.com/pallets). |
| spaCy and `en_core_web_sm` | MIT | English pronunciation/text normalization; model is downloaded separately. |
| Transformers, Hugging Face Hub, Safetensors, and tokenizers | Apache-2.0 or upstream package license | Model and checkpoint support; not every package is imported by each synthesis path. |
| Remaining pinned direct and resolved transitive Python packages | Their respective upstream licenses | `requirements.txt` pins direct packages and Git commits. Pip currently resolves transitive versions at setup time; consult each installed wheel's metadata and license file for its exact release. |

## Why PolyVoice uses GPL-3.0

The project intentionally licenses its own integrated application under GPL-3.0. The German phonemization route imports GPL-covered `phonemizer-fork` modules into the same Python process and uses eSpeak NG through that path. FSF guidance treats linking or binding a GPL library into one program as a combined work for distribution purposes. This is a conservative choice for the public source distribution; whether a particular packaging arrangement forms one combined work is fact-specific. It does not mean all packages or model weights become GPL: each keeps its own license, and this repository does not relicense third-party assets. See the [GNU GPL FAQ on combining and linking](https://www.gnu.org/licenses/gpl-faq.en.html).

This notice is a project-level license summary, not legal advice. Before distributing a bundled binary, installer, or model files, review the exact licenses, notices, and redistribution terms for every included artifact. PolyVoice's setup downloads models locally and does not bundle them in Git.
