#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import mido


# In[2]:


def note_to_hex(note):
    # MIDI notes can range from 0 to 127, so we divide by 127 to get a value between 0 and 1
    note_normalized = note / 127.0
    # Multiply by 255 to get an RGB value between 0 and 255, then convert to hexadecimal
    return "{:02x}".format(int(note_normalized * 255))


# In[3]:


def hex_to_rgb(hex_color):
    # Remove the '#' from the start of the hex color if it's present
    hex_color = hex_color.lstrip('#')
    # Convert the hex color to RGB
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


# In[32]:


def convert_midi_to_rgb(file):
    if os.path.isfile(file):
        # Open the MIDI file
        midi_file = mido.MidiFile(file)
        color_tracks = []

        # Loop over all tracks
        for track in midi_file.tracks:
            # Loop over all messages in track
            track_color = []
            for i, msg in enumerate(track):
                if msg.type == 'note_on':                  
                    rgb = ["ff", "ff", "ff"] if i % 3 > 0 else ["00", "00", "00"]
                    rgb[i % 3] = note_to_hex(msg.note)
                    color_tracks.append(hex_to_rgb("#" + ''.join(rgb)))

        return color_tracks
    else:
        raise Exception("File does not exist.")


# In[ ]:


def convert_midi_to_rgb2(file):
    if os.path.isfile(file):
        # Open the MIDI file
        midi_file = mido.MidiFile(file)
        color_tracks = []

        # Loop over all tracks
        for track in midi_file.tracks:
            # Loop over all messages in track
            track_color = ""
            for msg in track:
                if msg.type == 'note_on':
                    track_color += note_to_hex(msg.note)
                    
                    if len(track_color) > 5:
                        color_tracks.append(hex_to_rgb("#" + track_color))
                        track_color = ""

        return color_tracks
    else:
        raise Exception("File does not exist.")