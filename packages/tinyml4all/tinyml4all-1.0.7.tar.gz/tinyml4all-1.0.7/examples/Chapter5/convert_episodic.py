import pickle

with open("sample_data/MediaControlChain.pkl", "rb") as f:
    chain = pickle.load(f)
    chain.convert_to(
        "c++", class_name="MediaControlChain", save_to="sample_data/MediaControlChain.h"
    )
