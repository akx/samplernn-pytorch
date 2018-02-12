import argparse, zipfile, os, shutil

ap = argparse.ArgumentParser()
ap.add_argument('-d', '--output-dir', required=True)
ap.add_argument('input', nargs='+')
args = ap.parse_args()

for input in args.input:
	with zipfile.ZipFile(input) as zf:
		for zi in zf.infolist():
			if zi.is_dir():
				continue
			if os.path.basename(zi.filename).startswith('._'):  # macOS metadata
				continue
			dest_name = os.path.join(args.output_dir, zi.filename)
			os.makedirs(os.path.dirname(dest_name), exist_ok=True)
			with open(dest_name, 'wb') as outfp:
				with zf.open(zi) as infp:
					shutil.copyfileobj(infp, outfp)