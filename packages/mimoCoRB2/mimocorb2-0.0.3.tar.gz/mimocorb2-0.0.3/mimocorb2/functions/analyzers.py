from mimocorb2 import Processor, BufferIO
import scipy.signal as signal


def pha(buffer_io: BufferIO):
    """mimoCoRB2 Function: Pulse Height Analysis using scipy.signal.find_peaks

    Analyzes pulse heights in a given channel of the input data using `scipy.signal.find_peaks`.
    This function processes the input data to find peaks and their properties based on the provided
    configuration parameters. Depending on the configuration, it can return various peak properties
    such as heights, thresholds, prominences, widths, and plateau sizes (see SciPy documentation).

    Type
    ----
    Processor

    Buffers
    -------
    sources
        1 source buffer containing the input data with multiple channels
    sinks
        1 with data_length = 1
        Possible field names:
            - position
            - peak_heights
                If `height` is specified in the config, the height of each peak in the specified channel.
            - left_thresholds, right_thresholds
                If `threshold` is specified, the left and right thresholds of each peak.
            - prominences, left_bases, right_bases
                If `prominence` is specified, the prominence of each peak, and its bases.
            - widths, width_heights, left_ips, right_ips
                If `width` is specified, the full width at the specified relative height.
            - plateau_sizes, left_edges, right_edges
                If `plateau_size` is specified, the size and edges of the peak plateau.
    observes
        0

    Configs
    -------
    channel : str, optional (default = 'first channel')
        Channel name to analyze. If not specified, the first channel in the input will be used.
    height : float, optional (default = None)
        Minimum height of peaks. If None, peak heights are not calculated.
    threshold : float, optional (default = None)
        Minimum vertical distance to neighbors. If None, thresholds are not calculated.
    distance : int, optional (default = None)
        Minimum number of samples between neighboring peaks.
    prominence : float, optional (default = None)
        Minimum prominence of peaks.
    width : float, optional (default = None)
        Minimum width of peaks.
    wlen : int, optional (default = None)
        Window length for prominence and width calculation.
    rel_height : float, optional (default = 0.5)
        Relative height for width calculation (default = 0.5).
    plateau_size : float, optional (default = None)
        Minimum size of the plateau at the peak.
    """

    processor = Processor(buffer_io)
    if len(buffer_io.data_out_examples) != 1:
        raise ValueError("mimocorb2.analyzers.pha only supports one sink.")
    data_in = buffer_io.data_in_examples[0].copy()
    data_out = buffer_io.data_out_examples[0].copy()

    config = processor.config
    channel = config.get('channel', data_in.dtype.names[0])
    height = config.get('height', None)
    threshold = config.get('threshold', None)
    distance = config.get('distance', None)
    prominence = config.get('prominence', None)
    width = config.get('width', None)
    wlen = config.get('wlen', None)
    rel_height = config.get('rel_height', 0.5)
    plateau_size = config.get('plateau_size', None)

    channels = data_in.dtype.names
    if channel not in channels:
        raise ValueError(f"Channel {channel} is not available in the source.")

    requested_parameters = data_out.dtype.names
    if data_out.size != 1:
        raise ValueError("mimocorb2.analyzers.pha only data_length = 1 in the sink.")

    for parameter in requested_parameters:
        if parameter in ['position']:
            pass
        elif parameter in ['peak_heights']:
            if height is None:
                raise ValueError(f"Parameter {parameter} is only possible with height config")
        elif parameter in ['left_thresholds', 'right_thresholds']:
            if threshold is None:
                raise ValueError(f"Parameter {parameter} is only possible with threshold config")
        elif parameter in ['prominences', 'left_bases', 'right_bases']:
            if prominence is None:
                raise ValueError(f"Parameter {parameter} is only possible with prominence config")
        elif parameter in ['widths', 'width_heights', 'left_ips', 'right_ips']:
            if width is None:
                raise ValueError(f"Parameter {parameter} is only possible with width config")
        elif parameter in ['plateau_sizes', 'left_edges', 'right_edges']:
            if plateau_size is None:
                raise ValueError(f"Parameter {parameter} is only possible with plateau_size config")
        else:
            raise ValueError(f"Parameter {parameter} is not supported")

    def ufunc(data):
        peaks, properties = signal.find_peaks(
            x=data[channel],
            height=height,
            threshold=threshold,
            distance=distance,
            prominence=prominence,
            width=width,
            wlen=wlen,
            rel_height=rel_height,
            plateau_size=plateau_size,
        )
        for i in range(len(peaks)):
            for parameter in requested_parameters:
                if parameter in ['position']:
                    data_out['position'] = peaks[i]
                else:
                    data_out[parameter] = properties[parameter][i]
            return [data_out]

    processor(ufunc)
