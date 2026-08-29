# -*- coding: utf-8 -*-
"""Fill an .hwpx form/template by replacing exact <hp:t> text nodes, repackage
so it remains a valid OWPML file (mimetype stored first)."""
import sys, zipfile, shutil, os

def fill(src, dst, replacements, section="Contents/section0.xml"):
    tmp = dst + ".work"
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    os.makedirs(tmp)
    names = []
    with zipfile.ZipFile(src) as z:
        names = z.namelist()
        z.extractall(tmp)
    # edit section xml
    p = os.path.join(tmp, section)
    xml = open(p, encoding="utf-8").read()
    for old, new in replacements:
        tag_old = f"<hp:t>{old}</hp:t>"
        tag_new = f"<hp:t>{new}</hp:t>"
        if tag_old not in xml:
            print("  !! not found:", repr(old))
        else:
            xml = xml.replace(tag_old, tag_new)
    open(p, "w", encoding="utf-8").write(xml)
    # repackage: mimetype first, stored
    if os.path.exists(dst):
        os.remove(dst)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        if "mimetype" in names:
            z.write(os.path.join(tmp, "mimetype"), "mimetype", compress_type=zipfile.ZIP_STORED)
        for n in names:
            if n == "mimetype":
                continue
            z.write(os.path.join(tmp, n), n)
    shutil.rmtree(tmp)
    print("wrote", dst)


if __name__ == "__main__":
    pass
