# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3.9.12 ('ele')
#     language: python
#     name: python3
# ---

# # Explore experimental metadata and processed data
#
# This notebook will describe the steps for interacting with the data ingested into `workflow-array-ephys`.

import os
if os.path.basename(os.getcwd()) == "notebooks": os.chdir("..")

# +
import datajoint as dj
import matplotlib.pyplot as plt
import numpy as np

from workflow_array_ephys.pipeline import lab, subject, session, ephys

# + [markdown] pycharm={"name": "#%% md\n"}
# ## Workflow architecture
#
# This workflow is assembled from 4 DataJoint elements:
#
# # + [element-lab](https://github.com/datajoint/element-lab)
# # + [element-animal](https://github.com/datajoint/element-animal)
# # + [element-session](https://github.com/datajoint/element-session)
# # + [element-array-ephys](https://github.com/datajoint/element-array-ephys)
#
# For the architecture and detailed descriptions for each of those elements, please visit the respective links.
#
# Below is the diagram describing the core components of the fully assembled pipeline.
#
# -

dj.Diagram(ephys) + (dj.Diagram(session.Session) + 1) - 1

# ## Browsing the data with DataJoint query and fetch
#
#
# DataJoint provides abundant functions to query data and fetch. For a detailed tutorials, visit our [general tutorial site](https://playground.datajoint.io/)
#

# Running through the pipeline, we have ingested data of subject6 session1 into the database. Here are some highlights of the important tables.

# ### `Subject` and `Session` tables

subject.Subject()

session.Session()

session_key = (
    session.Session & 'subject="subject6"' & 'session_datetime = "2021-01-15 11:16:38"'
).fetch1("KEY")

# ### `ephys.ProbeInsertion` and `ephys.EphysRecording` tables
#
# These tables stores the probe recordings within a particular session from one or more probes.

ephys.ProbeInsertion & session_key

ephys.EphysRecording & session_key

# ### `ephys.ClusteringTask` , `ephys.Clustering`, and `ephys.CuratedClustering`
#
# + Spike-sorting is performed on a per-probe basis with the details stored in `ClusteringTask` and `Clustering`
#
# + After the spike sorting, a copy of `Clustering` entry was inserted into `CuratedClustering`.
#
# + For manual curation options, please visit the [electrophysiology description page](https://elements.datajoint.org/description/array_ephys/)

ephys.ClusteringTask & session_key

# In our example workflow, `curation_output_dir` is the same as `clustering_output_dir`

ephys.CuratedClustering & session_key

# ### Waveform
#
# Spike-sorting results are stored in `ephys.CuratedClustering` and `ephys.WaveformSet.Waveform`

ephys.CuratedClustering.Unit & session_key

# Let's pick one probe insertion and one `insertion_number`, and further inspect the clustering results.

insertion_key = (
    ephys.CuratedClustering & session_key & "insertion_number = 0"
).fetch1("KEY")

ephys.CuratedClustering.Unit & insertion_key

# ### Generate a raster plot

# Let's try a raster plot for a subset of units

subset = ephys.CuratedClustering.Unit & 'unit IN ("6","7","9","14","15","17","19")'
subset

units, unit_spiketimes = (subset).fetch("unit", "spike_times")

x = np.hstack(unit_spiketimes)
y = np.hstack([np.full_like(s, u) for u, s in zip(units, unit_spiketimes)])

fig, ax = plt.subplots(1, 1, figsize=(32, 8))
ax.plot(x, y, "|")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Unit")

# ### Plot waveform of a unit

# Let's pick one unit and further inspect

unit_key = (subset & "unit = 15").fetch1("KEY")

ephys.CuratedClustering.Unit * ephys.WaveformSet.Waveform & unit_key

unit_data = (
    ephys.CuratedClustering.Unit * ephys.WaveformSet.PeakWaveform & unit_key
).fetch1()

unit_data

sampling_rate = (ephys.EphysRecording & insertion_key).fetch1(
    "sampling_rate"
) / 1000  # in kHz
plt.plot(
    np.r_[: unit_data["peak_electrode_waveform"].size] * 1 / sampling_rate,
    unit_data["peak_electrode_waveform"],
)
plt.xlabel("Time (ms)")
plt.ylabel(r"Voltage ($\mu$V)")

# ## Summary and Next Step

# This notebook highlights the major tables in the workflow and visualize some of the ingested results.
#
# The next notebook [06-drop](06-drop-optional.ipynb) shows how to drop schemas and tables if needed.
