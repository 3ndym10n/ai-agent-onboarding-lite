class AiOnboardError(Exception):
    pass


class PolicyError(AiOnboardError):
    pass


class GuardBlocked(AiOnboardError):
    pass


def err(code: str, msg: str, **k):
    out = {"ok": False, "code": code, "message": msg}
    out.update(k or {})
    return out


def ok(**k):
    out = {"ok": True}
    out.update(k or {})
    return out

