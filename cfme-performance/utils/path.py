from py.path import local
import os

_this_file = os.path.abspath(__file__)

project_path = local(_this_file).new(basename='..')
conf_path = project_path.join('conf')
log_path = project_path.join('log')
results_path = project_path.join('results')


def get_rel_path(absolute_path_str):
    """Get a relative path for object in the project root

    Args:
        absolute_path_str: An absolute path to a file anywhere under `project_path`

    Note:

        This will be a no-op for files that are not in `project_path`

    """
    target_path = local(absolute_path_str)
    # relto returns empty string when no path parts are relative
    return target_path.relto(project_path) or absolute_path_str
