import re

BEGIN_DOCUMENT = r"\begin{document}"
END_DOCUMENT = r"\end{document}"

SETHEADER_RE = re.compile(r"\\setheader\{(.+)\}")
SUBFILE_RE = re.compile(r"\\subfile\{(.+?)\}")
