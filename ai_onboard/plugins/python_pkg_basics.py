import os
def check_requirements(root):
    return os.path.exists(os.path.join(root, "requirements.txt"))
