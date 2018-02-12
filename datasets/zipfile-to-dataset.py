import zipfile
import os
import sys
import shutil
import tempfile
import numpy
import argparse
from librosa.core import load
from librosa.output import write_wav

def read_samples_from_zip(zf, sr):
    sounds = {}
    for file in zf.namelist():
        if '._' in file:  # OSX metafile
            continue
        ext = os.path.splitext(file)[1]
        if ext not in ('.wav', '.ogg'):
            continue
        with tempfile.NamedTemporaryFile(suffix=ext) as outfp:
            with zf.open(file) as zipfp:
                shutil.copyfileobj(zipfp, outfp)
                outfp.flush()
            sound, _ = load(outfp.name, sr=sr, mono=True)
            sounds[file] = numpy.trim_zeros(sound)
            print('Loaded', file)
    return sounds

def generate_slices(sounds, sr, slice_length):
    concatenated = numpy.concatenate(list(sounds.values()))
    slice_in_samples = int(sr * slice_length)
    num_slices = len(concatenated) / slice_in_samples
    end_offset = int(num_slices) * slice_in_samples  # In order to get equivalent-length samples, we'll discard some samples
    if end_offset != len(concatenated):
        print('Discarding {} samples from end'.format(len(concatenated) - end_offset))
    for offset in range(0, end_offset, slice_in_samples):
        slice = concatenated[offset : offset + slice_in_samples]
        assert len(slice) == slice_in_samples
        yield slice

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sample-rate', '-r', dest='sr', default=22050, type=int)
    ap.add_argument('--slice-length', '-l', dest='slice_length', default=1.0, type=float)
    ap.add_argument('--dest-path', '-d', required=True)
    ap.add_argument('--input-zip', '-i', required=True)
    args = ap.parse_args()
    with zipfile.ZipFile(args.input_zip) as zf:
        sounds = read_samples_from_zip(zf, sr=args.sr)
    for i, slice in enumerate(generate_slices(sounds, sr=args.sr, slice_length=args.slice_length)):
        pth = os.path.join(args.dest_path, '%04d.wav' % i)
        os.makedirs(os.path.dirname(pth), exist_ok=True)
        print('Writing:', pth)
        write_wav(pth, slice, sr=args.sr)

if __name__ == '__main__':
    main()