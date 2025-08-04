import glob

HEADER = """
## Source codes

This section contains the some source codes from sglang's sglrouter.

"""

FILE_TMPL = """### file: {path}

```{filetype}
{content}
```
"""


def gen_txt(path, filetype):
    with open(path) as f:
        content = f.read()
        return FILE_TMPL.format(
            path=path,
            filetype=filetype,
            content=content,
        )


def gen_header():
    with open("sgl-router/README.md") as f:
        return f.read() + "\n" + HEADER


def main():
    print(gen_header())

    paths = glob.glob("sgl-router/src/**/*.rs", recursive=True)
    for path in paths:
        print(gen_txt(path, "rust"))

    paths = glob.glob("sgl-router/py_src/sglang_router/*.py", recursive=True)
    for path in paths:
        print(gen_txt(path, "python"))

    paths = glob.glob("sgl-router/scripts//*.py", recursive=True)
    for path in paths:
        print(gen_txt(path, "python"))


if __name__ == "__main__":
    main()
