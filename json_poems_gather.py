import json
import os
import warnings


def read_json(inpath: str, poets_names: tuple):
    with open(inpath, "r") as f:
        data = json.load(f)

    if poets_names is None:
        poets_names = data.keys()

    text = ""
    for poet_name in poets_names:
        if poet_name not in data:
            warnings.warn(f"Poet {poet_name} not found in {inpath}")
            continue

        for poem_name, poem_dict in data[poet_name]["poems"].items():
            text += f"\t{poem_name}\t\n"
            text += poem_dict["text"].strip() + "\n\n"

    return text


def save_text(text: str, outpath: str):
    open_mode = "a" if os.path.exists(outpath) else "w"
    with open(outpath, open_mode) as f:
        f.write(text)


def main(in_path: str, poets_names: tuple, outpath: str):
    text = read_json(in_path, poets_names)
    save_text(text, outpath)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--inpath', type=str, default="poets.json")
    parser.add_argument('--poets', type=str, nargs='+', default=None)
    parser.add_argument('--outpath', type=str, default="poems.txt")
    args = parser.parse_args()

    main(args.inpath, args.poets, args.outpath)
