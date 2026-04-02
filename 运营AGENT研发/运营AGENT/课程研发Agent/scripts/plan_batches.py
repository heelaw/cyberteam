#!/usr/bin/env python3
from __future__ import annotations

import json

BATCHES = [
    {
        "batch": "A",
        "courses": [
            "03-AI时代下的运营基石课",
            "互联网运营必备的底层心法",
            "SOP与项目管理常识",
            "用户洞察与需求定位",
        ],
    },
    {
        "batch": "B",
        "courses": [
            "10-运营必学：从根本上提升你的流量、用户敏锐度与洞察",
            "08-运营必学：一切营销推广、转化链路的设计关键原则",
            "17-运营必学营销推广",
            "营销推广基本功",
        ],
    },
    {
        "batch": "C",
        "courses": [
            "07-深刻理解4种常见的运营数据漏斗",
            "06-从0到100，不同业务如何思考宏观运营操盘节奏",
            "内容运营的基本功",
            "高阶活动运营",
        ],
    },
]

print(json.dumps(BATCHES, ensure_ascii=False, indent=2))
