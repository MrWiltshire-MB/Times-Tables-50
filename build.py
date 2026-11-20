"""Build the GitHub Pages version from the live app.
index.html  = live app + online sign-in and saving (src/auth.js + src/app-cloud.js)
teacher.html = teacher page (src/teacher.html + src/auth.js)
Usage: python3 build.py [path/to/times-tables.html] [out_dir]
"""
import re, sys, os
here = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/times-tables.html"
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "out")
os.makedirs(out, exist_ok=True)
app = open(src).read()
auth = open(os.path.join(here, "src/auth.js")).read()
cloud = open(os.path.join(here, "src/app-cloud.js")).read()

hook = '  show("homeView");\n})();'
assert app.count(hook) == 1, "hook point not found"
app = app.replace(hook, '  show("homeView");\n' + auth + cloud + '})();')
head = ('<!doctype html>\n<html lang="en-AU">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n</head>\n<body>\n')
open(os.path.join(out, "index.html"), "w").write(head + app + "\n</body>\n</html>\n")

# Teacher page: colour tokens, parts and homework weeks come from the app so they stay in step
tokens = re.search(r":root \{.*?\n:root\[data-theme=\"dark\"\] \{.*?\}\n", app, re.S).group(0)
me = app[app.index("const ME_SUBS = "):]; me = me[:me.index("];")]
parts = re.findall(r'\["(10[A-L])", "', me)
hw = re.search(r"const HOMEWORK = \[(.*?)\n  \];", app, re.S).group(1)
hw_js = "[" + hw + "]"
t = open(os.path.join(here, "src/teacher.html")).read()
t = t.replace("/*TOKENS*/", tokens).replace("/*AUTH*/", auth).replace("/*PARTS*/", repr(parts).replace("'", '"')).replace("/*HOMEWORK*/", hw_js)
open(os.path.join(out, "teacher.html"), "w").write(t)
for f in ("index.html", "teacher.html"):
    s = open(os.path.join(out, f)).read()
    assert "__tt" not in s and "271828" not in s and "service_role" not in s, f
print("built", out, parts)
