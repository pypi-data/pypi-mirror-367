from mimocorb2 import Exporter

import numpy as np
from numpy.lib import recfunctions as rfn
import pandas as pd
import time


def drain(buffer_io):
    """mimoCoRB2 Function: Drain buffer

    Drains all data from the source buffer and does nothing with it.

    Type
    ----
    Exporter

    Buffers
    -------
    sources
        1
    sinks
        0
    observes
        0
    """
    exporter = Exporter(buffer_io)
    for data, metadata in exporter:
        pass


def histogram(buffer_io):
    """mimoCoRB2 Function: Export data as a histogram.

    Saves histograms of the data in the source buffer to npy files in the run_dir for each field in the source buffer.
    The histograms are saved in a directory named "Histograms_<source_buffer_name>".
    The directory contains a file named "info.csv" with the histogram configuration and individual npy files for each channel.
    It is possible to visualize the histograms using the `visualize_histogram` function.

    Type
    ----
    Exporter

    Buffers
    -------
    sources
        1 with data_length = 1
    sinks
        Pass through data without modification to all sinks. Must share same dtype as source buffer.
    observes
        0

    Configs
    -------
    update_interval : int, optional (default=1)
        Interval in seconds to save the histogram data to files.
    bins : dict
        Dictionary where keys are channel names and values are tuples of (min, max, number_of_bins).
        Channels must be present in the source buffer data.

    Examples
    --------
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> import pandas as pd
    >>> info_df = pd.read_csv('info.csv')
    >>> bins = {ch: np.linspace(info_df['Min'][i], info_df['Max'][i], info_df['NBins'][i]) for i, ch in enumerate(info_df['Channel'])}
    >>> for ch in info_df['Channel']:
    ...     data = np.load(f'{ch}.npy')
    ...     plt.plot(bins[ch][:-1], data, label=ch)
    >>> plt.legend()
    >>> plt.show()
    """
    exporter = Exporter(buffer_io)

    # Get info from the buffer
    name = buffer_io.buffer_names_in[0]
    data_example = buffer_io.data_in_examples[0]
    available_channels = data_example.dtype.names

    if data_example.size != 1:
        raise ValueError('histogram exporter only supports data_length = 1')

    directory = buffer_io.run_dir / f"Histograms_{name}"
    directory.mkdir(parents=True, exist_ok=True)

    # Get config
    update_interval = exporter.config.get('update_interval', 1)
    bin_config = exporter.config['bins']

    requested_channels = bin_config.keys()
    for rch in requested_channels:
        if rch not in available_channels:
            raise ValueError(f"Channel '{rch}' not found in the data")
    channels = requested_channels

    info_df = pd.DataFrame(
        {
            'Channel': channels,
            'Min': [bin_config[ch][0] for ch in channels],
            'Max': [bin_config[ch][1] for ch in channels],
            'NBins': [bin_config[ch][2] for ch in channels],
        }
    )
    info_df.to_csv(directory / 'info.csv', index=False)

    bins = {}
    hists = {}
    files = {}
    for ch in channels:
        files[ch] = directory / f"{ch}.npy"
        bins[ch] = np.linspace(bin_config[ch][0], bin_config[ch][1], bin_config[ch][2])
        hists[ch] = np.histogram([], bins=bins[ch])[0]

    def save_hists():
        for ch in channels:
            np.save(files[ch], hists[ch])

    save_hists()

    last_save = time.time()
    for data, metadata in exporter:
        for ch in channels:
            hists[ch] += np.histogram(data[ch], bins=bins[ch])[0]

        if time.time() - last_save > update_interval:
            save_hists()
            last_save = time.time()
    save_hists()


def csv(buffer_io):
    """mimoCoRB2 Function: Save data from the source buffer to a CSV file.

    Saves data from the source buffer to a CSV file in the run_dir.
    Each field in the source buffer is saved as a column in the CSV file.

    Type
    ----
    Exporter

    Buffers
    -------
    sources
        1 with data_length = 1
    sinks
        Pass through data without modification to all sinks. Must share same dtype as source buffer.
    observes
        0

    Configs
    -------
    save_interval : int, optional (default=1)
        Interval in seconds to save the CSV file.
    filename : str, optional (default='buffer_name')
        Name of the CSV file to save the data to. The file will be saved in the run_dir.

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> print(pd.read_csv('run_directory/exporter_name.csv'))
    """
    exporter = Exporter(buffer_io)
    data_example = exporter.data_example
    metadata_example = exporter.metadata_example

    run_dir = exporter.run_dir
    buffer_name = buffer_io.buffer_names_in[0]

    config = exporter.config
    save_interval = config.get('save_interval', 1)
    filename = config.get('filename', buffer_name)
    filename = run_dir / f"{filename}.csv"

    if data_example.size != 1:
        raise ValueError('csv exporter only supports data_length = 1')

    header = []
    for dtype_name in metadata_example.dtype.names:
        header.append(dtype_name)

    for dtype_name in data_example.dtype.names:
        header.append(dtype_name)

    # create empty dataframe
    df = pd.DataFrame(columns=header)
    df.to_csv(filename, index=False)
    count = 0

    last_save = time.time()
    count = 0
    for data, metadata in exporter:
        count += 1
        line = np.append(rfn.structured_to_unstructured(metadata), rfn.structured_to_unstructured(data))
        df.loc[count] = line
        if time.time() - last_save > save_interval:
            df.to_csv(filename, index=False, mode='a', header=False)
            last_save = time.time()
            df = pd.DataFrame(columns=header)
            count = 0

    df.to_csv(filename, index=False, mode='a', header=False)
