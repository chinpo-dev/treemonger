import os
import magic

from utils import format_bytes


class TreeNode(object):
    def __init__(self, path, size=0):
        self.path = path
        self.size = size
        self.children = []
        self.details = {}

    @property
    def name(self):
        name = os.path.basename(self.path)
        if os.path.isdir(self.path):
            name += os.sep
        return name

    def __str__(self):
        size = format_bytes(self.size)
        info_list = [size]
        if self.children:
            children = '%d children' % len(self.children)
            info_list.append(children)

        if 'lines' in self.details:
            details = '%d lines' % self.details['lines']
            info_list.append(details)

        info = ', '.join(info_list)
        return '<%s: %s>' % (self.name, info)

    def __repr__(self):
        return self.__str__()


def print_directory_tree(t, L=0, max=3):
    """print to stdout"""
    if L < max:
        print('%s%s' % ('  ' * L, t))
        if os.path.isdir(t.path):
            for child in t.children:
                print_directory_tree(child, L + 1)


def tree_to_dict(t):
    return {
        'path': t.path,
        'size': t.size,
        'details': t.details,
        'children': [tree_to_dict(c) for c in t.children],
    }


def _get_directory_tree(sd, exclude_dirs=[], slow_details=False):
    t = TreeNode(sd.path)
    size = 0

    if sd.is_dir(follow_symlinks=False):
        # directory
        if sd.path in exclude_dirs:
            return None
        try:
            for file in os.scandir(sd.path):
                subtree = _get_directory_tree(file, exclude_dirs)
                if subtree:
                    t.children.append(subtree)
                    size += t.children[-1].size
        except PermissionError:
            print("failed to access " + sd.path)

    else:
        # file
        size = sd.stat(follow_symlinks=False).st_size
        if slow_details:
            t.details = get_file_details(sd.path)

    t.size = size
    return t

def get_directory_tree(path, exclude_dirs=[], slow_details=False):
    t = TreeNode(path)
    sd = os.scandir(path) 
    i = 0
    for file in sd:
        t.children.append(_get_directory_tree(file, exclude_dirs))
        t.size += t.children[-1].size
        i+=1
    return t

def get_file_details(path):
    ftype = magic.from_file(path).lower()
    details = {}
    if 'ascii' in ftype:
        details['lines'] = get_line_count(path)

    return details


def get_line_count(path):
    with open(path, 'r') as f:
        content = f.readlines()
    return len(content)


if __name__ == '__main__':
    py_path = os.getenv('PY')
    t = get_directory_tree(py_path)
    print_directory_tree(t)


########################################
# deprecated
def print_treemap_dict(t, L=0, max=3, printfiles=True):
    # prints a formatted list as returned by gettree

    if L < max:
        name = os.path.basename(t['path'])

        if os.path.isdir(t['path']):
            name += os.sep

        print('%s%s: %s' % ('  ' * L, name, t['bytes']))

        if os.path.isdir(t['path']):
            for child in t['children']:
                print_treemap_dict(child, L + 1)


def get_treemap_dict(path):
    t = {'path': path,
         'bytes': 0}

    if os.path.islink(path):
        return t

    bytes = 0
    if os.path.isdir(path):
        try:
            t['children'] = []
            # for file in scandir(path)  # TODO: use this - http://benhoyt.com/writings/scandir/
            for file in os.listdir(path):
                t['children'].append(get_treemap_dict(path + os.path.sep + file))
                bytes += t['children'][-1]['bytes']
        except OSError as exc:
            print('ignoring OSError at %s' % path)

    elif os.path.isfile(path):
        bytes = os.path.getsize(path)

    t['bytes'] = bytes
    return t
