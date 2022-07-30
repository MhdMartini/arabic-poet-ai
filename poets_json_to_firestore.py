from tqdm import tqdm
import firebase_admin
from firebase_admin import firestore
import json
import os


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--cred', type=str, default="cred.json",
                        help="path to GCP credentials json file")
    parser.add_argument('--update_with', type=str,
                        help="url to poets json file", required=True)
    args = parser.parse_args()

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = args.cred
    firebase_admin.initialize_app()
    db = firestore.client()

    with open(args.update_with) as f:
        update_dict = json.load(f)

    for poet_name, poet_data in tqdm(update_dict.items()):

        poems = poet_data.pop('poems')

        # update poet shallow data
        db.collection("poets").document(poet_name).set(poet_data)

        # update poet's poems subcollection
        for poem_title, poem_data in poems.items():
            db.collection("poets").document(poet_name).collection(
                "poems").document(poem_title).set(poem_data)
