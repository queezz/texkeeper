import argparse
import importlib.machinery
import sys
import types
from pathlib import Path


def _bootstrap_package():
    if "keeper" in sys.modules:
        return

    package_root = Path(__file__).resolve().parent
    module = types.ModuleType("keeper")
    module.__file__ = str(package_root / "__init__.py")
    module.__path__ = [str(package_root)]
    module.__package__ = "keeper"
    spec = importlib.machinery.ModuleSpec("keeper", loader=None, is_package=True)
    spec.submodule_search_locations = [str(package_root)]
    module.__spec__ = spec
    sys.modules["keeper"] = module


def main():
    _bootstrap_package()
    from keeper.commands import add_section, clean, init, init_config, pdf, watch

    parser = argparse.ArgumentParser(
        prog="keeper.py",
        description=(
            "keeper.py — a small caretaker for a LaTeX thinking workspace\n\n"
            "Typical workflow:\n"
            "  python keeper.py init\n"
            "  latexmk master.tex\n"
            "  python keeper.py clean\n"
            "  python keeper.py pdf\n\n"
            "PDF options:\n"
            "  python keeper.py pdf --overwrite  overwrite existing PDFs in ./PDFs\n"
            "\n"
            "Section helpers:\n"
            '  python keeper.py add-section 31-work-in-progress "Work in Progress"'
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser(
        "init",
        help="initialize project structure (safe to re-run)",
        description=init.run.__doc__,
    )

    sub.add_parser(
        "init-config",
        help="generate default texkeeper.toml configuration file",
        description=init_config.run.__doc__,
    )

    sub.add_parser(
        "clean",
        help="remove LaTeX temporary files",
        description=clean.run.__doc__,
    )

    sub.add_parser(
        "watch",
        help="watch configured paths for file changes",
        description=watch.run.__doc__,
    )

    pdf_parser = sub.add_parser(
        "pdf",
        help="copy PDFs to ./PDFs",
        description=pdf.run.__doc__,
    )
    pdf_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="overwrite existing PDFs in ./PDFs",
    )
    add_section_parser = sub.add_parser(
        "add-section",
        help="register a new chapter section and stub file",
        description=add_section.run.__doc__,
    )
    add_section_parser.add_argument(
        "slug",
        help="slug used for the chapter filename (e.g. 20-permeation-gas-driven-multilayer-membrane)",
    )
    add_section_parser.add_argument(
        "title",
        help="header text for \\setheader and the default \\section within the chapter",
    )

    sub.add_parser(
        "help",
        help="show this help message",
    )

    args = parser.parse_args()

    if args.cmd == "init":
        init.run()
    elif args.cmd == "init-config":
        init_config.run()
    elif args.cmd == "clean":
        clean.run()
    elif args.cmd == "watch":
        watch.run()
    elif args.cmd == "pdf":
        pdf.run(args.overwrite)
    elif args.cmd == "add-section":
        add_section.run(args.slug, args.title)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
