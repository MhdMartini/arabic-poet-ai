import firebase_admin
from firebase_admin import firestore
import os


def read_db(cred: str, poets: tuple):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred
    firebase_admin.initialize_app()
    db = firestore.client()
    text = ""
    if poets is None:
        iter = db.collection("poets").stream()
    else:
        iter = db.collection("poets").where("name", "in", poets).stream()

    for poet in iter:
        for peom in poet.reference.collection("poems").stream():
            poem_dict = peom.to_dict()
            text += '\t' + poem_dict["title"] + '\t\n'
            text += poem_dict["text"].strip() + '\n\n'
    return text


def save_text(text: str, filename: str):
    with open(filename, "w") as f:
        f.write(text)


def main(cred: str, poets: tuple, outpath: str):
    text = read_db(cred, poets)
    save_text(text, outpath)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--cred', type=str, default="cred.json")
    parser.add_argument('--poets', type=str, nargs='+', default=None)
    parser.add_argument('--outpath', type=str, default="poems.txt")
    args = parser.parse_args()

    main(args.cred, args.poets, args.outpath)
