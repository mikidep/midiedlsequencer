# MIDI EDL Sequencer

Generates EDL timelines from MIDI files.

## TL;DR:

TODO: place image here

## In detail:

MIDI EDL Sequencer is a Python 3 script that generates EDL Timelines from a MIDI file, translating MIDI notes to video clips. The user produces a YAML file specifying various samples, as in the following example:

```yaml
 - name: kick
   note: C1
   src: bd deep.mov
   start: 0.729
   length: 0.321

 - name: rim
   note: C#1
   src: click.mov
   start: 9.813
   length: 0.144

 - name: snare
   note: D1
   src: pop.mov
   start: 2.765
   length: 0.143

 - name: snare2
   note: E1
   src: click.mov
   start: 22.666
   length: 0.603
```

For each of these samples an EDL file named according to the ```name``` attribute is generated, which represents a timeline with a single track, on which video clips are positioned on times matching the occurences of the specified note. Each video clip has the specified source (```src```), cut according to the ```start``` and ```length``` attributes (in seconds). The EDL file can then be imported in a video editor (only tested on DaVinci Resolve), in which video clips with corresponding filenames have been imported.

The purpose of this script is to aid the editing of videos involving samples taken from, or otherwise associated to, video clips, where one wants to have the clips appear on time with some MIDI sequencing of the corresponding samples.

## Installation (from source)

First, get [Poetry](https://python-poetry.org/) if not already installed. Then:

```sh
git clone https://github.com/mikidep/midiedlsequencer.git
cd midiedlsequencer
poetry build --format wheel
python -m pip install dist/midiedlsequencer*.whl
```

Note that the pip script path (usually ```~/.local/bin```) should be in your ```$PATH```.

## Usage

```sh
midiedlsequencer --help
```

```
MIDI EDL Sequencer
Generates EDL timelines from MIDI files.

Usage:
  midiedlsequencer -s SAMPLES_FILE -m MIDI_FILE -o OUTPUT_FOLDER [--middle-c MIDDLE_C] [--fps FPS]
  midiedlsequencer (-h | --version)

Options:
  -h --help             Show this screen.
  --version             Show version.
  -s SAMPLES_FILE       Samples description YAML file.
  -m MIDI_FILE          Input MIDI sequence file
  -o OUTPUT_FOLDER      Output folder for EDL files.
  --middle-c MIDDLE_C   The name of middle C, aka MIDI note 60. Must be either C3 or C4. [default: C3]
  --fps FPS             The FPS setting for the resulting timelines. [default: 30.0]
```

For example:

```sh
midiedlsequencer -s samples.yml -m dm.mid -o edl/
```

```sh
midiedlsequencer -s samples.yml -m dm.mid -o edl --middle-c C4 --fps 24
```



