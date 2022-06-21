Keyword2User = {
    "fangkai": "焦方锴",
    "xiaolin": "陈潇琳",
    "sunwei": "孙玮",
    "muhe": "丁沐河",
    "zhenyang": "李振阳",
    "wangkun": "王锟",
    "tianyang": "田阳",
    "junshuo": "张峻硕",
    "ziyang": "马子阳",
    "leigang": "曲磊钢",
    "zhaishuyan": "翟书言"
}

def infer_user(cmd):
    for keyword, user in Keyword2User.items():
        if keyword in cmd:
            return user
    return "Unknown"