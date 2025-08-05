import mne
import os
import sys
from typing import List

# Get the absolute path of the parent directory of the current script
parent_dir = os.path.dirname(os.getcwd())
gradparent_dir = os.path.dirname(parent_dir)

# Add the parent directory to sys.path
sys.path.append(parent_dir)
sys.path.append(gradparent_dir)

from meg_qc.plotting.universal_plots import get_tit_and_unit 

# Keep imports in this order! 

def make_howto_use_plots_section (metric: str):

    """
    Make HTML section explaining how to use figures.

    Parameters
    ----------
    metric: str
        Metric name like "ECG', "MUSCLE', ...

    Returns
    -------
    html_section_str : str
        The html string of how-to section of the report.
    
    """

    how_to_dict = {
        'STIMULUS': 'All figures are interactive. Hover over an element to see more information.',
        'ECG': 'All figures are interactive. Hover over an element to see more information. <br> Sensors positions plot: Click and drag the figure to turn it. Enlarge the figure by running two fingers on the touchpad, or scrolling with "Ctrl" on the mouse. <br> Click and select a part of the figure to enlarge it. Click "Home" button on the righ upper side to return to the original view. <br> With one click on the name in a legend on the right side you can select/deselect an element. <br> With a double click you can select/deselect a whole group of elements related to one lobe area.',
        'STD': 'All figures are interactive. Hover over an element to see more information. <br> Sensors positions plot: Click and drag the figure to turn it. Enlarge the figure by running two fingers on the touchpad, or scrolling with "Ctrl" on the mouse. <br> Click and select a part of the figure to enlarge it. Click "Home" button on the righ upper side to return to the original view. <br> With one click on the name in a legend on the right side you can select/deselect an element. <br> With a double click you can select/deselect a whole group of elements related to one lobe area. <br> Figure with multiple bars can be enlarged by using the scrolling element on the bottom.',
        'PSD': 'All figures are interactive. Hover over an element to see more information. <br> Sensors positions plot: Click and drag the figure to turn it. Enlarge the figure by running two fingers on the touchpad, or scrolling with "Ctrl" on the mouse. <br> Click and select a part of the figure to enlarge it. Click "Home" button on the righ upper side to return to the original view. <br> With one click on the name in a legend on the right side you can select/deselect an element. <br> With a double click you can select/deselect a whole group of elements related to one lobe area.',
        'MUSCLE': 'All figures are interactive. Hover over an element to see more information. <br> Click and select a part of the figure to enlarge it. Click "Home" button on the righ upper side to return to the original view.',
        'HEAD': 'All figures are interactive. Hover over an element to see more information. <br> Click and select a part of the figure to enlarge it. Click "Home" button on the righ upper side to return to the original view.',
        'EOG': 'All figures are interactive. Hover over an element to see more information. <br> Sensors positions plot: Click and drag the figure to turn it. Enlarge the figure by running two fingers on the touchpad, or scrolling with "Ctrl" on the mouse. <br> Click and select a part of the figure to enlarge it. Click "Home" button on the righ upper side to return to the original view. <br> With one click on the name in a legend on the right side you can select/deselect an element. <br> With a double click you can select/deselect a whole group of elements related to one lobe area.',
        'PTP_MANUAL': 'All figures are interactive. Hover over an element to see more information. <br> Sensors positions plot: Click and drag the figure to turn it. Enlarge the figure by running two fingers on the touchpad, or scrolling with "Ctrl" on the mouse. <br> Click and select a part of the figure to enlarge it. Click "Home" button on the righ upper side to return to the original view. <br> With one click on the name in a legend on the right side you can select/deselect an element. <br> With a double click you can select/deselect a whole group of elements related to one lobe area. <br> Figure with multiple bars can be enlarged by using the scrolling element on the bottom.',
    }

    if metric not in how_to_dict:
        return ''

    how_to_section="""
        <!-- *** Section *** --->
        <center>
        <h4>"""+'How to use figures'+"""</h4>
        """ + how_to_dict[metric]+"""
        <br></br>
        <br></br>
        </center>"""

    return how_to_section


def make_metric_section(fig_derivs_metric: List, section_name: str, report_strings: dict):
    
    """
    Create 1 section of html report. 1 section describes 1 metric like "ECG" or "EOG", "Head position" or "Muscle"...
    Functions does:

    - Add section title
    - Add user notification if needed (for example: head positions not calculated)
    - Loop over list of derivs belonging to 1 section, keep only figures
    - Put figures one after another with description under. Description should be set inside of the QC_derivative object.

    Parameters
    ----------
    fig_derivs_metric : List
        A list of QC_derivative objects belonging to 1 metric and containing figures.
    section_name : str
        The name of the section like "ECG" or "EOG", "Head position" or "Muscle"...
    report_strings : dict
        A dictionary with strings to be added to the report: general notes + notes about every measurement (when it was not calculated, for example). 
        This is not a detailed description of the measurement.

    Returns
    -------
    html_section_str : str
        The html string of 1 section of the report.
    """


    # Define a mapping of section names to report strings and how-to-use plots
    section_mapping = {
        'INITIAL_INFO': ['Data info', report_strings['INITIAL_INFO']],
        'ECG': ['ECG: heart beat interference', f"<p>{report_strings['ECG']}</p>"],
        'EOG': ['EOG: eye movement interference', f"<p>{report_strings['EOG']}</p>"],
        'HEAD': ['Head movement', f"<p>{report_strings['HEAD']}</p>"],
        'MUSCLE': ['High frequency (Muscle) artifacts', f"<p>{report_strings['MUSCLE']}</p>"],
        'STD': ['Standard deviation of the data', f"<p>{report_strings['STD']}</p>"],
        'PSD': ['Frequency spectrum', f"<p>{report_strings['PSD']}</p>"],
        'PTP_MANUAL': ['Peak-to-Peak manual', f"<p>{report_strings['PTP_MANUAL']}</p>"],
        'PTP_AUTO': ['Peak-to-Peak auto from MNE', f"<p>{report_strings['PTP_AUTO']}</p>"],
        'SENSORS': ['Sensors locations', "<p></p>"],
        'STIMULUS': ['Stimulus channels', f"<p>{report_strings['STIMULUS']}</p>"]
    }

    # Determine the content for the section
    section_header = section_mapping[section_name][0] #header
    section_content = section_mapping[section_name][1] #intro text

    # Add figures to the section intro
    if fig_derivs_metric:
        for fig in fig_derivs_metric:
            section_content += fig.convert_fig_to_html_add_description()
    else:
        section_content = "<p>This measurement has no figures. Please see csv files.</p>"


    metric_section = f"""
        <!-- *** Section *** --->
        <center>
        <h2>{section_header}</h2>
        {section_content}
        <br></br>
        <br></br>
        </center>"""

    return metric_section

def make_sensor_figs_section(sensor_fig_derivs: List):

    """
    Create a section with sensor positions.
    
    Parameters
    ----------
    sensor_fig_derivs : List
        A list of QC_derivative objects belonging to 1 section with only sensors positions.
        Normally should be only 1 figure or none.
    
    Returns
    -------
    sensor_section : str
        The html string of 1 section with sensors positions.
    """
    
    sensor_section = ''
    if sensor_fig_derivs:
        for fig in sensor_fig_derivs:
            sensor_section += fig.convert_fig_to_html_add_description()

    sensor_html = """
        <!-- *** Section *** --->
        <center>
        """ + sensor_section + """
        <br></br>
        <br></br>
        </center>
        """

    return sensor_html

def combine_howto_sensors_and_metric(derivs_section: List, metric_name: str, report_strings: dict):
    
    """
    Create a section (now used as the entire report for 1 metric).
    On top: how to use figures
    Then: Metric name and description, notes.
    Main part: figures with descriptions.
    
    Parameters
    ----------
    derivs_section : List
        A list of QC_derivative objects belonging to 1 section.
    section_name : str
        The name of the section like "ECG" or "EOG", "Head position" or "Muscle"...
    report_strings : dict
        A dictionary with strings to be added to the report: general notes + notes about every measurement (when it was not calculated, for example). 
        This is not a detailed description of the measurement.
    
    Returns
    -------
    html_section_str : str
        The html string of 1 section of the report.
    """

    sensor_fig_derivs, fig_derivs_metric = keep_fig_derivs(derivs_section)

    how_to_section = make_howto_use_plots_section(metric_name)
    sensor_section = make_sensor_figs_section(sensor_fig_derivs)
    metric_section = make_metric_section(fig_derivs_metric, metric_name, report_strings)

    combined_section = how_to_section + sensor_section + metric_section

    return combined_section


def keep_fig_derivs(derivs_section:list):

    """
    Loop over list of derivs belonging to 1 section, keep only figures to add to report.
    
    Parameters
    ----------
    derivs_section : List
        A list of QC_derivative objects belonging to 1 section.
        
    Returns
    -------
    fig_derivs_section : List
        A list of QC_derivative objects belonging to 1 section with only figures.
    sensor_fig_derivs : List
        A list of QC_derivative objects belonging to 1 section with only sensors positions.
        Normally should be only 1 figure or none.
    """
    
    fig_derivs_metric = [d for d in derivs_section if d.content_type in {'plotly', 'matplotlib'} and 'SENSORS' not in d.name.upper()]
    sensor_fig_derivs = [d for d in derivs_section if d.content_type in {'plotly', 'matplotlib'} and 'SENSORS' in d.name.upper()]

    return sensor_fig_derivs, fig_derivs_metric


def make_joined_report(sections: dict, report_strings: dict):

    """
    Create report as html string with all sections. Currently make_joined_report_mne is used.
    This one is plain report, without mne fance wrapper.

    Parameters
    ----------
    sections : dict
        A dictionary with section names as keys and lists of QC_derivative objects as values.
    sreport_strings : dict
        A dictionary with strings to be added to the report: general notes + notes about every measurement (when it was not calculated, for example). 
        This is not a detailed description of the measurement.
    

    Returns
    -------
    html_string : str
        The html whole string of the report.
    
    """


    header_html_string = """
    <!doctype html>
    <html>
        <head>
            <meta charset="UTF-8">
            <title>MEG QC report</title>
            <style>body{ margin:0 100;}</style>
        </head>
        
        <body style="font-family: Arial">
            <center>
            <h1>MEG data quality analysis report</h1>
            <br></br>
            """+ report_strings['SHIELDING'] + report_strings['M_OR_G_SKIPPED'] + report_strings['EPOCHING']

    main_html_string = ''
    for key in sections:

        html_section_str = make_metric_section(derivs_section = sections[key], section_name = key, report_strings = report_strings)
        main_html_string += html_section_str


    end_string = """
                     </center>
            </body>
        </html>"""


    html_string = header_html_string + main_html_string + end_string

    return html_string


def make_joined_report_mne(raw_info_path: str, sections:dict, report_strings: dict):

    """
    Create report as html string with all sections and embed the sections into MNE report object.

    Parameters
    ----------
    raw_info_path : str
        Path to the raw info file.
    sections : dict
        A dictionary with section names as keys and lists of QC_derivative objects as values.
    report_strings : dict
        A dictionary with strings to be added to the report: general notes + notes about every measurement (when it was not calculated, for example). 
        This is not a detailed description of the measurement.
    default_settings : dict
        A dictionary with default settings.
    

    Returns
    -------
    report : mne.Report
        The MNE report object with all sections.
    
    """

    report = mne.Report(title=' MEG QC Report')
    # This method also accepts a path, e.g., raw=raw_path
    if raw_info_path: #if info present
        info_loaded = mne.io.read_info(raw_info_path)
        info_html = info_loaded._repr_html_()
        # Wrap the HTML content in a centered div
        centered_info_html = f"""
        <div style="text-align: center;">
            {info_html}
        </div>
        """
        report.add_html(centered_info_html, 'Info about the Original raw file (not filtered, not resampled)')

    for key, values in sections.items():
        key_upper = key.upper()
        if values and key_upper != 'REPORT' and key_upper != 'Report MNE' and key_upper != 'Simple_metrics':
            #html_section_str = make_metric_section(derivs_section = sections[key_upper], section_name = key, report_strings = report_strings)
            html_section_str = combine_howto_sensors_and_metric(derivs_section = sections[key_upper], metric_name = key_upper, report_strings = report_strings)
            report.add_html(html_section_str, title=key_upper)

    return report


def simple_metric_basic(metric_global_name: str, metric_global_description: str, metric_global_content_mag: dict, metric_global_content_grad: dict, metric_local_name: str =None, metric_local_description: str =None, metric_local_content_mag: dict =None, metric_local_content_grad: dict =None, display_only_global: bool =False, psd: bool=False, measurement_units: bool = True):
    
    """
    Basic structure of simple metric for all measurements.
    
    Parameters
    ----------
    metric_global_name : str
        Name of the global metric.
    metric_global_description : str
        Description of the global metric.
    metric_global_content_mag : dict
        Content of the global metric for the magnitometers as a dictionary.
        Content is created inside of the module for corresponding measurement.
    metric_global_content_grad : dict
        Content of the global metric for the gradiometers as a dictionary.
        Content is created inside of the module for corresponding measurement.
    metric_local_name : str, optional
        Name of the local metric, by default None (in case of no local metric is calculated)
    metric_local_description : str, optional
        Description of the local metric, by default None (in case of no local metric is calculated)
    metric_local_content_mag : dict, optional 
        Content of the local metric for the magnitometers as a dictionary, by default None (in case of no local metric is calculated)
        Content is created inside of the module for corresponding measurement.
    metric_local_content_grad : dict, optional
        Content of the local metric for the gradiometers as a dictionary, by default None (in case of no local metric is calculated)
        Content is created inside of the module for corresponding measurement.
    display_only_global : bool, optional
        If True, only global metric is displayed, by default False
        This parameter is set to True in case we dont need to display any info about local metric at all. For example for muscle artifacts.
        In case we want to display some notification about local metric, but not the actual metric (for example it failed to calculate for a reason), 
        this parameter is set to False and metric_local_description should contain that notification and metric_local_name - the name of missing local metric.
    psd : bool, optional
        If True, the metric is done for PSD and the units are changed accordingly, by default False
    measurement_units : bool, optional
        If True, the measurement units are added to the metric, by default True

    Returns
    -------
    simple_metric : dict
        Dictionary with the whole simple metric to be converted into json in main script.
        
    """
    
    _, unit_mag = get_tit_and_unit('mag', psd=psd)
    _, unit_grad = get_tit_and_unit('grad', psd=psd)

    if display_only_global is False:
       m_local = {metric_local_name: {
            "description": metric_local_description,
            "mag": metric_local_content_mag,
            "grad": metric_local_content_grad}}
    else:
        m_local = {}


    if measurement_units is True:

        simple_metric={
            'measurement_unit_mag': unit_mag,
            'measurement_unit_grad': unit_grad,
            metric_global_name: {
                'description': metric_global_description,
                "mag": metric_global_content_mag,
                "grad": metric_global_content_grad}
            }
    else:
        simple_metric={
            metric_global_name: {
                'description': metric_global_description,
                "mag": metric_global_content_mag,
                "grad": metric_global_content_grad}
            }

    #merge local and global metrics:
    simple_metric.update(m_local)

    return simple_metric