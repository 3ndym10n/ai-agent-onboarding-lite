import argparse
def main():
    p = argparse.ArgumentParser(prog="ai_onboard")
    sub = p.add_subparsers(dest="cmd", required=True)
    for c in ["analyze","charter","plan","align","change","validate","kaizen","optimize"]:
        sub.add_parser(c)
    args = p.parse_args()
    print(f"Executed {args.cmd}")
