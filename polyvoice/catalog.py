"""UI voice catalog for locally verified synthesis voices."""

MAX_TEXT_LENGTH = 10_000

LANGUAGES = [
    {"id": "en-us", "label": "English (American)", "enabled": True},
    {"id": "en-gb", "label": "English (British)", "enabled": True},
    {"id": "de", "label": "German — Deutsch", "enabled": True},
    {"id": "ja", "label": "Japanese — 日本語", "enabled": True},
    {"id": "zh", "label": "Mandarin Chinese — 中文", "enabled": True},
]


def _voice(voice_id, name, gender):
    return {"id": voice_id, "name": name, "gender": gender, "enabled": True}


VOICES = {
    "en-us": [
        _voice("af_heart", "Heart", "Female"), _voice("af_alloy", "Alloy", "Female"),
        _voice("af_aoede", "Aoede", "Female"), _voice("af_bella", "Bella", "Female"),
        _voice("af_jessica", "Jessica", "Female"), _voice("af_kore", "Kore", "Female"),
        _voice("af_nicole", "Nicole", "Female"), _voice("af_nova", "Nova", "Female"),
        _voice("af_river", "River", "Female"), _voice("af_sarah", "Sarah", "Female"),
        _voice("af_sky", "Sky", "Female"), _voice("am_adam", "Adam", "Male"),
        _voice("am_echo", "Echo", "Male"), _voice("am_eric", "Eric", "Male"),
        _voice("am_fenrir", "Fenrir", "Male"), _voice("am_liam", "Liam", "Male"),
        _voice("am_michael", "Michael", "Male"), _voice("am_onyx", "Onyx", "Male"),
        _voice("am_puck", "Puck", "Male"), _voice("am_santa", "Santa", "Male"),
    ],
    "en-gb": [
        _voice("bf_alice", "Alice", "Female"), _voice("bf_emma", "Emma", "Female"),
        _voice("bf_isabella", "Isabella", "Female"), _voice("bf_lily", "Lily", "Female"),
        _voice("bm_daniel", "Daniel", "Male"), _voice("bm_fable", "Fable", "Male"),
        _voice("bm_george", "George", "Male"), _voice("bm_lewis", "Lewis", "Male"),
    ],
    "de": [
        _voice("martin", "Martin", "Male"),
        _voice("victoria", "Victoria", "Female"),
    ],
    "ja": [
        _voice("jf_alpha", "Alpha", "Female"), _voice("jf_gongitsune", "Gongitsune", "Female"),
        _voice("jf_nezumi", "Nezumi", "Female"), _voice("jf_tebukuro", "Tebukuro", "Female"),
        _voice("jm_kumo", "Kumo", "Male"),
    ],
    "zh": [
        _voice("zf_xiaobei", "Xiaobei", "Female"), _voice("zf_xiaoni", "Xiaoni", "Female"),
        _voice("zf_xiaoxiao", "Xiaoxiao", "Female"), _voice("zf_xiaoyi", "Xiaoyi", "Female"),
        _voice("zm_yunjian", "Yunjian", "Male"), _voice("zm_yunxi", "Yunxi", "Male"),
        _voice("zm_yunxia", "Yunxia", "Male"), _voice("zm_yunyang", "Yunyang", "Male"),
    ],
}
