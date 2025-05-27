import torch
import torchaudio
import torch.nn.functional as F
from torch.nn.utils.rnn import pad_sequence
from ASV_System.resnet_models import se_res2net50_v1b
from ASV_System.db_utils import save_embedding_to_postgres, load_embedding_from_postgres
import speechbrain as sb

# register - username , path 3
# verify - username , path 1
MODEL_ASV_PATH = "src/Weights/ASV_model.pth"

run_opts = {
    "device": "cuda" if torch.cuda.is_available() else "cpu"
}

def load_wavs(file_list, target_sample_rate=16000):
    wavs = []
    for file in file_list:
        sig, fs = torchaudio.load(file)
        if fs != target_sample_rate:
            resampler = torchaudio.transforms.Resample(fs, target_sample_rate)
            sig = resampler(sig)
        sig = sig.mean(dim=0)  # Convert to mono
        wavs.append(sig)
    return wavs

# Compute embeddings from waveforms
def compute_embedding(wavs, model):
    with torch.no_grad():
        lengths = [len(wav) for wav in wavs]
        max_length = max(lengths)
        wav_lens = torch.tensor([l / max_length for l in lengths], dtype=torch.float32).to(run_opts["device"])

        # Pad wavs to create a batch tensor
        padded_wavs = pad_sequence(wavs, batch_first=True)  # Shape: [batch, time]
        padded_wavs = padded_wavs.to(run_opts["device"])

        feats = sb.lobes.features.MFCC(n_mfcc=24, n_mels=44, deltas=False, context=False).to(run_opts["device"])
        normalization = sb.processing.features.InputNormalization(norm_type="sentence", std_norm=False).to(run_opts["device"])

        features = feats(padded_wavs)
        feats = normalization(features, wav_lens)

        if features.dim() == 3:
            features = features.unsqueeze(1)
            # add print statement to check the shape
            print(f"Features shape after unsqueeze when dim =3: {features.shape}")

        embeddings = model.extract(features)
        embeddings = embeddings.squeeze(1)
        # add print statement to check the shape
        print(f"Final shape inside compute_embedding: {embeddings.shape}")
    return embeddings


def compute_mean_enrol_embedding(username, enrol_files, model):
    speaker_embeddings = {}
    with torch.no_grad():
        for enrol_file in enrol_files:
            enrol_wav = load_wavs([enrol_file])
            enrol_emb = compute_embedding(enrol_wav, model).unsqueeze(1) 
            # add print statement to check the shape
            print(f"Enrolment embedding shape for {enrol_file}: {enrol_emb.shape}") 

            if username not in speaker_embeddings:
                speaker_embeddings[username] = []
            speaker_embeddings[username].append(enrol_emb)
    
    # Compute the mean embedding for the speaker
    if username in speaker_embeddings:
        emb_list = speaker_embeddings[username]
        mean_embedding = torch.stack(emb_list).mean(dim=0)
        # add print statement to check the shape
        print(f"Mean embedding shape for {username}: {mean_embedding.shape}")
        return username, mean_embedding
    else:
        raise ValueError(f"No enrolment files found for user: {username}")

def create_test_embedding(username, test_file, model):
    test_wav = load_wavs([test_file])
    test_emb = compute_embedding(test_wav, model).unsqueeze(1) 
    # add print statement to check the shape
    print(f"Test embedding shape for {test_file}: {test_emb.shape}")
    return username, test_emb

def score_cosine(emb_enrol, emb_test):
    emb_enrol = F.normalize(emb_enrol.squeeze(), dim=0)
    emb_test = F.normalize(emb_test.squeeze(), dim=0)
    return F.cosine_similarity(emb_enrol, emb_test, dim=0)


def load_model(ckpt_path):
    print("[INFO] Loading model...")
    model = se_res2net50_v1b(num_classes=1211)
    checkpoint = torch.load(ckpt_path, map_location=run_opts["device"])
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    model.to(run_opts["device"])
    return model

def register_user(username, path1, path2, path3):
    model = load_model(MODEL_ASV_PATH)
    enrol_files = [path1, path2, path3]
    _, mean_embedding = compute_mean_enrol_embedding(username, enrol_files, model)
    save_embedding_to_postgres(username, mean_embedding)
    print(f"[REGISTER] Registration successful for user: {username}")

def run_verification_from_db(username, test_file):
    model = load_model(MODEL_ASV_PATH)
    enrol_embedding = load_embedding_from_postgres(username).unsqueeze(1).to(run_opts["device"])
    _, test_embedding = create_test_embedding(username, test_file, model)
    score = score_cosine(enrol_embedding, test_embedding)
    print(f"[VERIFY] Cosine similarity score: {score.item():.4f}")
    return score.item()