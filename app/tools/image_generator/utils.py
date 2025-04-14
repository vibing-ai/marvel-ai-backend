unsafe_keywords = [
    # Hate Speech
    # (Remember to populate racial, ethnic, religious, and sexual orientation slurs carefully and comprehensively)
    "bitch", "cunt", "faggot", "dyke", "tranny", "shemale", "heshe",
    "retard", "cripple", "spaz", "fatso", "fatty", "skinny", "anorexic",
    "animal", "insect", "vermin", "disease",
    "kill [group]", "exterminate [group]", "genocide [group]", "hang [group]", "lynch [group]",
    "lazy [race]", "dumb [gender]", "greedy [ethnicity]", "violent [nationality]",
    "swastika", "SS", "white power", "black sun",

    # Sexually Explicit Content
    "sex", "intercourse", "fuck", "cock", "pussy", "vagina", "penis", "fellatio", "cunnilingus",
    "anal sex", "oral sex", "bondage", "domination", "submission", "rape", "incest", "bestiality",
    "dick", "tits", "boobs", "ass", "butt", "genitals", "breasts", "pubic", "scrotum", "vulva",
    "vibrator", "dildo", "sex toy", "fleshlight",
    "horny", "aroused", "wet", "hard", "cum", "orgasm", "climax",
    "porn", "pornographic", "xxx", "sex tape",
    "child porn", "underage sex", "forced sex", "trafficking (sexual)",
    "naked", "nude", "stripping", "lingerie", "revealing",
    "prostitute", "escort", "sex worker",
    "footjob", "handjob",

    # Violence and Gore
    "kill", "murder", "slaughter", "massacre", "execute", "assassinate", "dismember", "mutilate",
    "torture", "rape", "gore", "bloody", "bloodshed", "decapitate", "eviscerate",
    "gun", "pistol", "rifle", "shotgun", "knife", "blade", "sword", "bomb", "grenade", "missile", "weaponize",
    "shoot", "stab", "slash", "beat", "punch", "kick", "strangle", "drown", "burn", "explode",
    "blood", "guts", "entrails", "viscera", "hemorrhage",
    "dead body", "corpse", "rotting", "decaying", "lifeless",
    "I'll kill you", "gonna hurt you", "I will destroy",
    "abuse", "beatings", "assault", "battery",
    "crash (graphic)", "explosion (graphic)", "collision (graphic)",

    # Illegal Activities
    "cocaine", "heroin", "marijuana", "weed", "meth", "ecstasy", "LSD", "opioids", "crack", "наркотики",
    "illegal gun", "unregistered firearm", "bomb making", "weapon smuggling",
    "steal", "rob", "theft", "burglary", "heist",
    "assault", "battery", "fight (illegal)",
    "scam", "defraud", "cheat", "phishing",
    "hack", "cyberattack", "data breach",
    "terrorist", "jihad", "bomb (terrorism)", "attack",
    "child porn", "pedophile", "molestation", "underage (sexual)", "CSAM",
    "[racial slur] attack", "[religious group] beaten", # (Remember to replace placeholders)

    # Self-Harm/Harm to Others
    "suicide", "kill myself", "end my life", "commit suicide", "overdose (intentional)", "hanging", "slit wrists",
    "cut", "burn", "self-harm", "self-mutilation", "scratch (intentional harm)",
    "anorexia", "bulimia", "starve", "purge",
    "you should kill yourself", "go hurt",
    "suicide is the only way", "self-harm is brave",
    "kill [person]", "murder [person]", "homicide"
]