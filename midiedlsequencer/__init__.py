"""MIDI EDL Sequencer
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

"""

__version__ = "0.1.0"

from docopt import docopt
import yaml, schema
import mido, pretty_midi
import opentimelineio as otio
from opentimelineio.opentime import (TimeRange, RationalTime)
import os

def entrypoint():
    args = docopt(__doc__, version=f"midiedlsequencer {__version__}")
    if args["--middle-c"] not in ["C3", "C4"]:
        print("Error: --middle-c argument must be either C3 or C4.\n")
        print(__doc__)
        exit(1)

    with open(args['-s']) as inf:
        samples = yaml.load(inf, Loader=yaml.Loader)

    schema.Schema([{
        "name": str,
        "note": schema.Regex(r"[A-G](#|b)?-?\d+"),
        "src": str,
        "start": float,
        "length": float
    }]).validate(samples)

    mid = mido.MidiFile(args['-m'])

    # MIDI messages represent time in ticks relative to the previous
    # message. The following code recovers the absoulute time from
    # the beginning of the file in seconds. The MidiFile object computes
    # the time difference in seconds as it's iterated through, and returns
    # it in a property of the messages yielded by the iterator. I don't
    # like that it's stateful and somewhat obscure, but it works.
    abs_msgs = []
    acc_time = 0.0
    for msg in mid: 
        acc_time += msg.time 
        abs_msgs.append(msg.copy(time=acc_time))

    notes = [m for m in abs_msgs if m.type is 'note_on']

    try:
        fps = float(args['--fps'])
    except ValueError:
        print("Error: --fps argument must be a float literal.\n")
        print(__doc__)
        exit(1)

    def range_from_s_fps(start, dur, fps):
        return TimeRange(start_time=RationalTime.from_seconds(start).rescaled_to(fps),
                        duration=RationalTime.from_seconds(dur).rescaled_to(fps))

    for s in samples:
        # The following selects the times of the note corresponding to the sample.
        midi_note = pretty_midi.note_name_to_number(s['note']) + (12 if args['--middle-c'] == "C3" else 0)
        times = [n.time for n in notes if n.note == midi_note]

        # The following creates an EDL timeline with the times computed above.

        tl = otio.schema.Timeline(name=s['name'])
        track = otio.schema.Track()
        
        # DaVinci Resolve will automatically set the starting timecode for an imported
        # EDL timeline to the start of the first clip. This has the undesirable effect
        # of removing initial blank time. As a workaround, a clip with duration zero
        # is inserted at the beginning of the EDL file: DVR will not place a clip in
        # the timeline, but it will set the starting timecode correctly.
        zero_clip = otio.schema.Clip(name=s["src"],
                                    media_reference=otio.schema.ExternalReference(target_url=s["src"]),
                                    source_range=range_from_s_fps(0, 0, fps))
        track.append(zero_clip)

        clip = otio.schema.Clip(name=s["src"],      # This is the actual clip
                                media_reference=otio.schema.ExternalReference(target_url=s["src"]),
                                source_range=range_from_s_fps(s['start'], s['length'], fps))

        # Blank time in OTIO timelines is represented with gaps. To accomodate non-contiguous
        # samples, gaps with appropriate durations must be inserted between clips.
        used_time = 0.0
        for t in times:
            track.append(otio.schema.Gap(source_range=range_from_s_fps(0, t-used_time, fps)))
            track.append(clip.deepcopy())
            used_time = t + s['length']
        tl.tracks.append(track)
        otio.adapters.write_to_file(tl, os.path.join(args['-o'], s['name'] + '.edl'))