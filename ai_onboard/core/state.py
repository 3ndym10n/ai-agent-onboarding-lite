ORDER = ["unchartered","chartered","planned","aligned","executing","kaizen_cycle"]
def advance(st, target):
    if ORDER.index(target) >= ORDER.index(st["state"]):
        st["state"] = target
    return st
