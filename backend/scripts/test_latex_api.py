import requests

tex = r"""\documentclass{article}
\begin{document}
Hello World!
\end{document}
"""

print("Attempting to compile LaTeX using texlive.net...")
try:
    # texlive.net API expects file data in multipart/form-data
    files = {'filecontents[]': ('test.tex', tex)}
    data = {'filename[]': 'test.tex', 'engine': 'pdflatex', 'return': 'pdf'}
    res = requests.post("https://texlive.net/cgi-bin/latexcgi", files=files, data=data)
    
    if res.status_code == 200 and res.content.startswith(b'%PDF'):
        with open("test_latex.pdf", "wb") as f:
            f.write(res.content)
        print("Success! Downloaded PDF.")
    else:
        print(f"Failed: {res.status_code}")
except Exception as e:
    print("Error:", e)
