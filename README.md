# PolyVoice

## Proje tanıtımı / Project introduction

PolyVoice, Windows bilgisayarınızda İngilizce, Almanca, Japonca ve Mandarin Çincesi metinleri sese dönüştüren yerel bir masaüstü web uygulamasıdır. Flask sunucusu yalnızca bilgisayarınızda çalışır; konuşma, CPU üzerinde yerel modellerle üretilir.

PolyVoice is a local web application for Windows that turns English, German, Japanese, and Mandarin Chinese text into speech on your computer. Its Flask server runs only on your computer, and speech is synthesized locally with CPU models.

## Özellikler / Features

- Amerikan ve Britanya İngilizcesi, Almanca, Japonca ve Mandarin Çincesi konuşma.
- Doğrulanmış ses dosyaları bulunan dillerde kadın ve erkek sesleri.
- Yerel ses ön izlemeleri; ilk kullanımdan sonra önbelleğe alınır.
- 0,5× ile 1,5× arasında konuşma hızı kontrolü.
- Oynat/duraklat, baştan başlat, ileri/geri sar, ses düzeyi ve indirme kontrolleri bulunan WAV oynatıcı.
- Unicode metin girişi, karakter sayacı ve 10.000 karakter sınırı.
- Üretilen geçici ses dosyaları bir saat sonra silinir. Uygulama metinlerinizi saklamaz.
- Hesap, veritabanı, ücretli API veya bulut TTS hizmeti gerektirmez.

- Speech in American and British English, German, Japanese, and Mandarin Chinese.
- Female and male voices in languages where verified voice files are available.
- Local voice previews, cached after their first use.
- Speech speed control from 0.5× to 1.5×.
- A WAV player with play/pause, restart, forward/backward seeking, volume, and download controls.
- Unicode text input, a character counter, and a 10,000-character limit.
- Generated temporary audio files are deleted after one hour. The app does not store your text.
- No account, database, paid API, or cloud TTS service is required.

## Desteklenen diller ve sesler / Supported languages and voices

| Dil | Sesler | Motor |
| --- | --- | --- |
| İngilizce (Amerikan) | Kokoro Amerikan ses kataloğu (kadın ve erkek) | Sabitlenmiş semidark Kokoro / Misaki çatalları |
| İngilizce (Britanya) | Kokoro Britanya ses kataloğu (kadın ve erkek) | Sabitlenmiş semidark Kokoro / Misaki çatalları |
| Almanca | Martin (erkek), Victoria (kadın) | Almanca etkinleştirilmiş Kokoro ve Misaki çatallarıyla Kikiri German kontrol noktaları |
| Japonca | Alpha, Gongitsune, Nezumi, Tebukuro (kadın); Kumo (erkek) | Yerel pyopenjtalk ile sabitlenmiş semidark Kokoro çatallaması |
| Mandarin Çincesi | Xiaobei, Xiaoni, Xiaoxiao, Xiaoyi (kadın); Yunjian, Yunxi, Yunxia, Yunyang (erkek) | Sabitlenmiş semidark Kokoro / Misaki çatalları |

| Language | Voices | Engine |
| --- | --- | --- |
| English (American) | Kokoro American voice catalog (female and male) | Pinned semidark Kokoro / Misaki forks |
| English (British) | Kokoro British voice catalog (female and male) | Pinned semidark Kokoro / Misaki forks |
| German | Martin (male), Victoria (female) | Kikiri German checkpoints with German-enabled Kokoro and Misaki forks |
| Japanese | Alpha, Gongitsune, Nezumi, Tebukuro (female); Kumo (male) | Pinned semidark Kokoro fork with local pyopenjtalk |
| Mandarin Chinese | Xiaobei, Xiaoni, Xiaoxiao, Xiaoyi (female); Yunjian, Yunxi, Yunxia, Yunyang (male) | Pinned semidark Kokoro / Misaki forks |

Victoria, yalnızca hem model dosyası hem de ses paketi bulunduğunda listelenir. Kurulum bu iki dosyayı sabitlenmiş SHA-256 özetleriyle doğrular. Almanca modeller gerektiğinde yüklenir; böylece motor aynı anda iki büyük Almanca model dosyasını bellekte tutmaz.

Victoria is listed only when both her model file and voice pack are present. Setup verifies both files against pinned SHA-256 hashes. German models are loaded when needed, so the engine does not keep both large German model files in memory at the same time.

## Sistem gereksinimleri / System requirements

- 64 bit Windows 10 veya Windows 11.
- 64 bit Python 3.12. Uygun Python yoksa `setup.bat`, SHA-256 ile doğrulanan uv aracını ve Python 3.12.15 çalışma zamanını yalnızca proje klasörüne indirir; sistem Python ayarlarını değiştirmez.
- Kurulum sırasında paketleri ve model dosyalarını indirmek için internet bağlantısı.
- Kurulum indirmeleri ve açılmış dosyalar için yaklaşık 5 GB boş disk alanı önerilir.
- CPU yeterlidir. GPU isteğe bağlıdır ve varsayılan olarak kullanılmaz.

- 64-bit Windows 10 or Windows 11.
- 64-bit Python 3.12. If a suitable Python is not present, `setup.bat` downloads a SHA-256-verified uv helper and the Python 3.12.15 runtime into the project folder only; it does not change system Python settings.
- An internet connection to download packages and model files during setup.
- About 5 GB of free disk space is recommended for setup downloads and extracted files.
- A CPU is sufficient. A GPU is optional and is not used by default.

## İndirme / Download

GitHub deposunun ana sayfasında **Code** düğmesine, ardından **Download ZIP** seçeneğine tıklayın. ZIP dosyasını indirdikten sonra Windows Gezgini'nde ZIP dosyasına sağ tıklayıp **Tümünü Ayıkla** seçeneğini kullanın. Ayıklanan proje klasörünü bilgisayarınızda yazma izniniz olan bir konuma taşıyın.

On the GitHub repository page, click **Code**, then select **Download ZIP**. After the ZIP file downloads, right-click it in Windows File Explorer and choose **Extract All**. Move the extracted project folder to a location on your computer where you have permission to write files.

## Kurulum / Installation

1. Ayıklanan PolyVoice klasörünü açın.
2. `setup.bat` dosyasına çift tıklayın. Kurulumu internet bağlantınız varken başlatın ve komut penceresi tamamlanana kadar açık bırakın.
3. Betik Windows 10/11 x64 uyumluluğunu, Python standart kütüphanesini ve disk alanını kontrol eder; en az 8 GB RAM önerilir. Uygun Python 3.12 yoksa Git gerektirmeyen, SHA-256 ile doğrulanan uv aracını ve Python 3.12.15'i proje klasörüne indirir. Ardından `.venv` oluşturur.
4. CPU için PyTorch'u ve sabitlenmiş uygulama bağımlılıklarını kurar. Kokoro ve Misaki, Git gerektirmeyen sabit commit kaynak arşivlerinden alınır. eSpeak NG DLL'i ve Almanca sözlüğü `espeakng-loader` paketiyle sanal ortama gelir; sistem geneline eSpeak kurulmaz.
5. Kokoro ses dosyaları, İngilizce telaffuz modeli ve Kikiri German Martin/Victoria dosyaları indirilir. Boyutlar platforma ve mevcut önbelleklere göre değişir: bağımlılıklar yaklaşık 1,2–1,8 GB, Almanca modeller/ses paketleri 655 MB, proje içi Python 21 MB ve uv yaklaşık 15 MB'tır. Açma, önbellek ve geçici dosyalar için en az 5 GB boş alan bırakın.
6. Son olarak gerçek CPU WAV ve ses ön izleme kontrolleri Amerikan/Britanya İngilizcesi, Almanca Martin/Victoria, Japonca ve Mandarin Çincesinde çalıştırılır. Herhangi bir kontrol başarısız olursa betik başarı mesajı vermez.

Kurulum betiği internet/indirme hatası, yetersiz disk alanı, eksik Python standart kütüphanesi ya da uyumsuz sistem algılarsa anlaşılır hata verir ve pencereyi açık tutar. `start.bat`, proje içindeki `.venv\Scripts\python.exe` dosyasını kullanır; ortam veya bağımlılık eksikse `setup.bat` dosyasını yeniden çalıştırmanızı söyler. Betikler Git veya sistem geneline kurulmuş eSpeak NG gerektirmez; sistem Python ayarlarını, PATH'i veya Windows güvenlik ayarlarını değiştirmez.

1. Open the extracted PolyVoice folder.
2. Double-click `setup.bat`. Start setup while you are connected to the internet, and leave the command window open until it finishes.
3. The script checks Windows 10/11 x64 compatibility, the Python standard library, and free disk space; at least 8 GB RAM is recommended. If a suitable Python 3.12 is not present, it downloads a Git-free, SHA-256-verified uv helper and Python 3.12.15 into the project folder. It then creates `.venv`.
4. It installs CPU PyTorch and pinned application dependencies. Kokoro and Misaki come from commit-pinned source archives that do not require Git. The eSpeak NG DLL and German dictionary are installed through `espeakng-loader` into the virtual environment; eSpeak is not installed system-wide.
5. Kokoro voice files, the English pronunciation model, and Kikiri German Martin/Victoria files are downloaded. Sizes vary by platform and existing caches: dependencies are about 1.2–1.8 GB, German models/voice packs about 655 MB, project-local Python about 21 MB, and uv about 15 MB. Keep at least 5 GB free for extraction, caches, and temporary files.
6. Finally, real CPU WAV and voice-preview checks run for American/British English, German Martin/Victoria, Japanese, and Mandarin Chinese. If any check fails, setup does not report success.

The setup script displays a clear error and keeps the window open if there is an internet/download failure, insufficient disk space, a missing Python standard library, or an incompatible system. `start.bat` uses the project's own `.venv\Scripts\python.exe`; if the environment or a dependency is missing, it tells you to run `setup.bat` again. The scripts do not require Git or system-wide eSpeak NG, and they do not change system Python settings, `PATH`, or Windows security settings.

## Kullanım / Usage

1. PolyVoice klasöründe `start.bat` dosyasına çift tıklayın.
2. Komut penceresinde gösterilen yerel adresi tarayıcıda açın. Uygulama önce `127.0.0.1:5000` adresini dener; bu port doluysa `127.0.0.1:5001` ile `127.0.0.1:5100` arasında kullanılabilir bir port seçer. Her zaman konsolda yazan adresi kullanın.
3. Bir dil ve ses seçin. Metninizi giriş alanına yazın veya yapıştırın. Metin uzunluğu 10.000 karakteri aşamaz.
4. İsterseniz ses ön izleme düğmesini kullanın ve konuşma hızını ayarlayın. Ses üretmek için **Generate Audio** düğmesine basın.
5. Ses hazır olduğunda sayfanın altındaki oynatıcıdan dinleyin, konumunu değiştirin veya WAV dosyasını indirin.

Uygulama yalnızca `127.0.0.1` üzerinde dinler ve Flask hata ayıklama modu kapalıdır. Başka bir projeye ait sunucu sürecini kapatmaz.

1. Double-click `start.bat` in the PolyVoice folder.
2. Open the local address shown in the command window in your browser. The app tries `127.0.0.1:5000` first. If that port is occupied, it selects an available port between `127.0.0.1:5001` and `127.0.0.1:5100`. Always use the address printed in the console.
3. Select a language and voice. Type or paste your text into the input area. Text cannot exceed 10,000 characters.
4. Optionally use the voice preview button and adjust the speech speed. Click **Generate Audio** to synthesize speech.
5. When the audio is ready, listen in the player at the bottom of the page, seek to another position, or download the WAV file.

The app listens only on `127.0.0.1`, and Flask debug mode is disabled. It does not stop a server process belonging to another project.

## Uygulamayı kapatma / Shutting down the app

PolyVoice'u başlattığınız komut penceresine geçin ve `Ctrl+C` tuşlarına basın. Gerekirse ekrandaki kapatma isteğini onaylayın. Alternatif olarak yalnızca PolyVoice'u başlatan komut penceresini kapatabilirsiniz. Başka uygulamalara ait komut pencerelerini kapatmayın.

Switch to the command window that started PolyVoice and press `Ctrl+C`. Confirm the shutdown prompt if one appears. Alternatively, close only the command window that launched PolyVoice. Do not close command windows belonging to other applications.

## Çevrimdışı çalışma ve gizlilik / Offline use and privacy

İlk kurulum için internet gerekir. Kurulum başarıyla tamamlandıktan sonra modeller, ses paketleri, sözlükler ve İngilizce telaffuz modeli yerel olarak bulunur; seslendirme ve ses ön izleme internet bağlantısı olmadan çalışır. Bir sesin ön izleme WAV dosyası ilk kullanımında yerel olarak oluşturulur ve önbelleğe alınır.

PolyVoice metinlerinizi veya üretilen sesleri bir bulut hizmetine yüklemez. Metin kalıcı olarak saklanmaz; geçici ses dosyaları bir saat sonra silinir. Çalıştırma sırasında model indirilmesini önlemek için çıkarımda Hugging Face çevrimdışı modu kullanılır.

An internet connection is required for the initial setup. After setup completes successfully, models, voice packs, dictionaries, and the English pronunciation model are available locally; speech synthesis and voice previews work without an internet connection. A voice's preview WAV is created locally on first use and then cached.

PolyVoice does not upload your text or generated audio to a cloud service. Text is not stored persistently; temporary audio files are deleted after one hour. Hugging Face offline mode is used during inference to prevent model downloads while the app runs.

## Sık karşılaşılan sorunlar / Troubleshooting

- **Python bulunamadı:** İnternet bağlantınızı kontrol edin ve `setup.bat` dosyasını yeniden çalıştırın. Betik doğrulanmış uv aracını ve Python 3.12.15'i proje klasörüne hazırlamayı dener.
- **Kurulumda disk veya RAM uyarısı:** Paket/model kurulumu için en az 5 GB boş disk alanı gerekir; 8 GB veya üzeri RAM önerilir. Daha az RAM'de ses üretimi yavaşlayabilir veya başarısız olabilir.
- **Git veya eSpeak NG bulunmuyor:** Bunları sistem geneline kurmanız gerekmez. Kokoro/Misaki sabit commit arşivlerinden kurulur; eSpeak DLL'i sanal ortamdaki `espeakng-loader` paketinden gelir.
- **`start.bat` Flask dâhil bir paketin eksik olduğunu söylüyor:** PolyVoice klasöründeki `setup.bat` dosyasını çalıştırın ve bağımlılık doğrulamasının başarılı biçimde bitmesini bekleyin.
- **Kurulum indirme hatası veriyor:** İnternet bağlantınızı ve boş disk alanınızı kontrol edip `setup.bat` dosyasını tekrar çalıştırın. İndirmeler ve sanal ortam proje klasöründe tutulur.
- **Tarayıcı uygulamayı açamıyor:** `start.bat` konsolunda yazan tam yerel adresi kullanın. 5000 portu doluysa uygulama 5001–5100 aralığında başka bir port dener.
- **Python başlatma hatası oluşuyor:** `start.bat` konsolda o çalıştırmaya ait tanılama kayıt dosyasının yolunu gösterir. Kayıtlar proje içindeki `.tmp\diagnostics` klasörüne yazılır; hata tekrar ederse ilgili `.log` dosyasını incelemek için saklayın.

- **Python was not found:** Check your internet connection and run `setup.bat` again. The script attempts to prepare the verified uv helper and Python 3.12.15 inside the project folder.
- **Setup warns about disk space or RAM:** At least 5 GB of free disk space is required for package/model installation; 8 GB or more RAM is recommended. Synthesis may be slow or fail with less RAM.
- **Git or eSpeak NG is not installed:** You do not need to install either system-wide. Kokoro/Misaki are installed from commit-pinned source archives, and eSpeak's DLL is supplied by `espeakng-loader` inside the virtual environment.
- **`start.bat` reports a missing package, including Flask:** Run `setup.bat` in the PolyVoice folder and wait for dependency verification to finish successfully.
- **Setup reports a download error:** Check your internet connection and free disk space, then run `setup.bat` again. Downloads and the virtual environment are kept in the project folder.
- **The browser cannot open the app:** Use the full local address printed in the `start.bat` console. If port 5000 is occupied, the app tries another port from 5001 through 5100.
- **A Python startup error occurs:** `start.bat` prints the path to a diagnostic log for that run. Logs are written to `.tmp\diagnostics` inside the project; if the error happens again, keep the relevant `.log` file for investigation.

## Teknik bilgiler / Technical information

- **Arayüz ve sunucu:** Python 3.12, Flask, HTML5, CSS3 ve düz JavaScript.
- **Konuşma üretimi:** Kokoro ve Misaki çıkarım hatları, CPU PyTorch, SoundFile ve dile özgü fonetik işleme bileşenleri.
- **Japonca:** Japonca fonetik işleme için yerel pyopenjtalk-plus ve OpenJTalk sözlüğü kullanılır.
- **Almanca:** Kikiri German model dosyaları, Almanca etkinleştirilmiş Kokoro ve Misaki çatallarıyla çalışır.
- **eSpeak NG:** Almanca fonetik işleme için DLL ve sözlük dosyaları `espeakng-loader` ile sanal ortamda bulunur; sistem PATH'i veya ayrıca kurulum gerekmez.
- **Ağ erişimi:** Yerel Flask sunucusu yalnızca `127.0.0.1` adresine bağlanır. Ses üretimi istekleri eşzamanlı olarak sınırlandırılır; kullanıcı metni kalıcı depolamaya yazılmaz.
- **Kelime zamanlaması:** Bu sürüm doğrulanmış bir forced-alignment hattı içermediğinden kelime düzeyinde senkron takip sunmaz.

- **Interface and server:** Python 3.12, Flask, HTML5, CSS3, and vanilla JavaScript.
- **Speech synthesis:** Kokoro and Misaki inference pipelines, CPU PyTorch, SoundFile, and language-specific phonemizers.
- **Japanese:** Local pyopenjtalk-plus and the OpenJTalk dictionary are used for Japanese phonemization.
- **German:** Kikiri German model files run with German-enabled Kokoro and Misaki forks.
- **eSpeak NG:** Its DLL and dictionary files for German phonemization are supplied by `espeakng-loader` in the virtual environment; no system PATH change or separate installation is needed.
- **Network access:** The local Flask server binds only to `127.0.0.1`. Speech generation requests are limited to run one at a time; user text is not written to persistent storage.
- **Word timing:** This release does not provide word-level synchronized tracking because it does not include a verified forced-alignment pipeline.

### Ekran görüntüleri / Screenshots

İncelenmiş bir ekran görüntüsü hazır olduğunda bu bölüme eklenecektir. Şimdilik yer tutucu görsel kullanılmamaktadır.

Screenshots will be added here when a reviewed capture is available. No placeholder image is used for now.

### Bilinen sınırlamalar / Known limitations

- Ses üretimi CPU üzerinde çalışır ve özellikle uzun metinlerde birkaç saniye sürebilir.
- Japonca telaffuz yerel OpenJTalk sözlüğünü kullanır; az rastlanan adlar ve birden fazla şekilde okunabilen kanjiler amaçlanandan farklı telaffuz edilebilir.
- İsteğe bağlı pyopenjtalk Nani prozodi tahminleyicisi kurulu değildir. Japonca WAV üretimi standart yerel işlem hattıyla doğrulanmıştır.
- Ses ön izleme WAV dosyaları ilk kullanımda oluşturulur; bu nedenle bir ses için ilk ön izleme daha uzun sürebilir.
- Kurulum, doğrudan bağımlılık sürümlerini ve Git commit'lerini sabitler; geçişli bağımlılık sürümleri pip tarafından çözülür ve tam, tekrarlanabilir bir kilit dosyası oluşturulmaz.
- Doğrulanmış bir forced-alignment hattı bu sürümde bulunmadığından kelime düzeyinde zamanlama sağlanmaz.

- Synthesis runs on the CPU and can take several seconds, especially for longer text.
- Japanese pronunciation uses the local OpenJTalk dictionary; rare names and kanji with multiple possible readings may be pronounced differently than intended.
- The optional pyopenjtalk Nani prosody predictor is not installed. Japanese WAV generation was verified with the standard local pipeline.
- Voice preview WAV files are created on first use, so the first preview for a voice may take longer.
- Setup pins direct dependency versions and Git commits; pip resolves transitive dependency versions, so there is no fully reproducible lock file.
- Word-level timing is not provided because this release does not include a verified forced-alignment pipeline.

### Testler / Tests

API testlerini proje sanal ortamından çalıştırmak için:

To run the API tests from the project's virtual environment:

```bat
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Kurulum ve modeller tamamlandıktan sonra gerçek CPU WAV üretimi ve ön izleme kontrollerini çalıştırmak için:

After setup and model downloads are complete, run real CPU WAV generation and preview checks with:

```bat
.venv\Scripts\python.exe scripts\smoke_test.py
```

Her iki komut da yerel olarak çalışır. Smoke test sırasında üretilen WAV dosyaları geçicidir ve doğrulamadan sonra silinir.

Both commands run locally. WAV files created by the smoke test are temporary and are removed after validation.

## Modeller, kaynak gösterimi ve lisanslar / Models, attributions, and licenses

- [Kokoro](https://github.com/hexgrad/kokoro) ve [Misaki](https://github.com/hexgrad/misaki): Apache-2.0. Almanca desteği, `b96fef95e6a746495f92443fac7c688f90fc57fc` commit'indeki [semidark Kokoro çatallamasını](https://github.com/semidark/kokoro) ve `9cda9268309160120fffee216280a9ca83ac4644` commit'indeki [semidark Misaki çatallamasını](https://github.com/semidark/misaki) kullanır.
- [Kikiri German — Martin](https://huggingface.co/kikiri-tts/kikiri-german-martin) ve [Victoria](https://huggingface.co/kikiri-tts/kikiri-german-victoria): Model kartlarında Apache-2.0 lisansı belirtilmiştir. Model ağırlıkları ve ses paketleri yerel olarak indirilir; depoya eklenmez.
- [Kokoro model kartı](https://huggingface.co/hexgrad/Kokoro-82M), eğitim verisindeki Koniwa (`tnc`, CC BY 3.0) ve SIWIS (CC BY 4.0) kaynaklı CC BY lisanslı ses verilerine atıf yapar. Veri kaynağı ayrıntıları için model kartının atıf bölümüne bakın.
- [phonemizer](https://github.com/bootphon/phonemizer) / `phonemizer-fork`: GPL-3.0-or-later; Almanca fonetik işleme yolunda kullanılır. [eSpeak NG](https://github.com/espeak-ng/espeak-ng) de GPL-3.0 lisanslıdır ve bazı bileşenleri ayrı lisanslara tabidir. [espeakng-loader](https://github.com/thewh1teagle/espeakng-loader) MIT lisanslıdır.
- [pyopenjtalk-plus](https://github.com/tsukumijima/pyopenjtalk-plus): MIT lisanslı sarmalayıcıdır; içerdiği OpenJTalk, HTS ses varlıkları ve marine bileşenleri ayrı bildirimlere tabidir.
- PyTorch'un birden fazla lisansı kapsayan lisans ifadesinde Apache-2.0, BSD-2-Clause, BSD-3-Clause ve BSL-1.0 bulunur. NumPy, SoundFile, Flask ve diğer bağımlılıklar kendi upstream lisanslarına tabidir. Bileşen özeti için [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) dosyasına bakın.

- [Kokoro](https://github.com/hexgrad/kokoro) and [Misaki](https://github.com/hexgrad/misaki): Apache-2.0. German support uses the [semidark Kokoro fork](https://github.com/semidark/kokoro) at commit `b96fef95e6a746495f92443fac7c688f90fc57fc` and the [semidark Misaki fork](https://github.com/semidark/misaki) at commit `9cda9268309160120fffee216280a9ca83ac4644`.
- [Kikiri German — Martin](https://huggingface.co/kikiri-tts/kikiri-german-martin) and [Victoria](https://huggingface.co/kikiri-tts/kikiri-german-victoria): Their model cards state the Apache-2.0 license. Model weights and voice packs are downloaded locally and are not included in the repository.
- The [Kokoro model card](https://huggingface.co/hexgrad/Kokoro-82M) credits CC BY audio in its training data from Koniwa (`tnc`, CC BY 3.0) and SIWIS (CC BY 4.0). See the model card's attribution section for dataset source details.
- [phonemizer](https://github.com/bootphon/phonemizer) / `phonemizer-fork`: GPL-3.0-or-later; used by the German phonemization path. [eSpeak NG](https://github.com/espeak-ng/espeak-ng) is also GPL-3.0, and some of its components have separate licenses. [espeakng-loader](https://github.com/thewh1teagle/espeakng-loader) is MIT-licensed.
- [pyopenjtalk-plus](https://github.com/tsukumijima/pyopenjtalk-plus): an MIT-licensed wrapper; its bundled OpenJTalk, HTS voice assets, and marine components are subject to separate notices.
- PyTorch's multi-license expression includes Apache-2.0, BSD-2-Clause, BSD-3-Clause, and BSL-1.0. NumPy, SoundFile, Flask, and the remaining dependencies are subject to their own upstream licenses. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for a component summary.

Depodaki `LICENSE` dosyası GNU GPL-3.0 lisansını içerir. PolyVoice, Almanca fonetik işleme yolu aynı Python çalışma ortamında GPL kapsamındaki phonemizer kodunu içe aktarıp kullandığı ve eSpeak NG ilişkili bir Almanca çalışma zamanı bileşeni olduğu için GPL-3.0'ı tercih eder. Bu, bütünleşik uygulamanın dağıtımı için ihtiyatlı bir lisans tercihidir; GPL paketinin bulunması, her bağımsız bağımlılığın lisansını kendiliğinden değiştirmez. Her üçüncü taraf bileşen ve model kendi lisansına ve bildirimlerine tabi olmaya devam eder. Bu metin hukuki danışmanlık değildir; dağıtım yapanlar kullandıkları paketleme biçimini ve lisans metinlerini incelemelidir.

The repository's `LICENSE` file contains the GNU GPL-3.0 license. PolyVoice chooses GPL-3.0 because its German phonemization path imports and uses GPL-covered phonemizer code in the same Python runtime, and eSpeak NG is a related German runtime component. This is a conservative licensing choice for distributing the integrated application; the mere presence of a GPL package does not automatically change the license of every independent dependency. Each third-party component and model remains subject to its own license and notices. This text is not legal advice; distributors should review their packaging approach and the applicable license texts.
