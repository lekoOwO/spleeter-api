import os
import shutil
import pathlib
from spleeter.separator import Separator

TMP_DIR = os.getenv('TMP_DIR', '/tmp/spleeter-api/tmp')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', '/tmp/spleeter-api/output')

seperators = {
    'high_freq': {
        2: Separator('spleeter:2stems-16kHz'),
        4: Separator('spleeter:4stems-16kHz'),
        5: Separator('spleeter:5stems-16kHz')
    },
    'low_freq': {
        2: Separator('spleeter:2stems'),
        4: Separator('spleeter:4stems'),
        5: Separator('spleeter:5stems')
    }
}

def split(filepath, stems, uuid, high_freq=True):
    stems = int(stems)
    if not stems in [2, 4, 5]:
        raise ValueError

    global OUTPUT_DIR

    global seperators
    seperator = seperators['high_freq' if high_freq else 'low_freq'][stems]
    outdir = os.path.join(TMP_DIR, f'{uuid}', "")
    pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
    seperator.separate_to_file(filepath, outdir)

    tmp_zip_path = shutil.make_archive(uuid, 'zip', outdir)
    zip_path = os.path.join(OUTPUT_DIR, f'{uuid}.zip')
    shutil.move(tmp_zip_path, zip_path)

    shutil.rmtree(outdir)
    os.remove(filepath)
    return zip_path