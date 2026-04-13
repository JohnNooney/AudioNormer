# AudioNormer
A python script for batch normalization of mp3 collections. This script makes use of two Python libraries for its normalization process
- [pydub](https://github.com/jiaaro/pydub) - uses audio splicing for cutting out silence in the beginning/end of tracks
- [rgain3](https://github.com/chaudum/rgain3) - equalizes a collection of mp3 files to the same volume level

## Setup Guide
### Linux 
rgain3 required depenedencies
``` shell
$ apt install \
     gir1.2-gstreamer-1.0 \
     gstreamer1.0-plugins-base \
     gstreamer1.0-plugins-good \
     gstreamer1.0-plugins-bad \
     gstreamer1.0-plugins-ugly \
     python3 \
     python3-gi
```

pydub required dependecies
```
apt-get install ffmpeg libavcodec-extra
```

pydub and rgain3 install
```
pip install pydub rgain3
```
## Usage

```shell
python audio_normer.py <input_dir> [options]
```

| Option | Default | Description |
|---|---|---|
| `-o / --output-dir` | in-place | Write processed files here |
| `--silence-threshold` | `-50.0` | dBFS cutoff for silence detection |
| `--chunk-size` | `10` | ms chunk size for silence scan |
| `--skip-silence-strip` | — | Skip pydub silence trimming |
| `--skip-replaygain` | — | Skip rgain3 ReplayGain pass |

**Examples**

```shell
# normalize in place
python audio_normer.py ~/Music/Album

# write to separate folder, stricter silence threshold
python audio_normer.py ~/Music/Album -o ~/Music/Album_out --silence-threshold -40

# ReplayGain only (no silence trimming)
python audio_normer.py ~/Music/Album --skip-silence-strip
```

## Resources 
[Splitting Audio Files using Silence Detection](https://stackoverflow.com/questions/45526996/split-audio-files-using-silence-detection)
[ReplayGain](https://wiki.hydrogenaud.io/index.php/ReplayGain)
