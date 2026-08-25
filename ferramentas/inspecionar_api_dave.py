from __future__ import annotations

import inspect
import dave

for nome in ("Session", "Encryptor", "Decryptor", "SignatureKeyPair"):
    cls = getattr(dave, nome)
    print(f"[{nome}]")
    for metodo in dir(cls):
        if metodo.startswith("_"):
            continue
        atributo = getattr(cls, metodo)
        if callable(atributo):
            try:
                assinatura = inspect.signature(atributo)
            except (TypeError, ValueError):
                assinatura = "<assinatura não exposta>"
            print(f"{metodo}{assinatura}")
            doc = getattr(atributo, "__doc__", None)
            if doc:
                print("  doc=" + " ".join(doc.split()))
