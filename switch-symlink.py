import os
import errno
import sys


def atomic_symlink(target, link_name):
    tmpLink = target + '_tmp'
    os.symlink(target, tmpLink)
    os.rename(tmpLink, link_name)


def forced_symlink(target, link_name):
    try:
        os.symlink(target, link_name)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(link_name)
            os.symlink(target, link_name)


if __name__ == '__main__':
    """
    Constantly change symlink of `current` folder with even `a` or `b` folder
    by using a forced or an atomic symlink strategy.
    """
    try:
        strategy = sys.argv[1]
        if strategy not in ['forced', 'atomic']:
            raise IndexError
    except IndexError:
        sys.stderr.write('Strategy argument must be provided\n')
        sys.stderr.write('Usage : python switch-symlink.py {forced or atomic}\n')
        sys.exit(2)

    cwd = os.getcwd()
    current_folder = os.path.join(cwd, 'current')
    a_folder = os.path.join(cwd, 'a')
    b_folder = os.path.join(cwd, 'b')

    try:
        while True:
            target = os.readlink(current_folder)

            if target == a_folder:
                new_target = b_folder
            else:
                new_target = a_folder

            print('Switching `current` to %s whith %s strategy' % (new_target, strategy))
            if strategy == 'forced':
                forced_symlink(new_target, current_folder)
            elif strategy == 'atomic':
                atomic_symlink(new_target, current_folder)

    except KeyboardInterrupt as e:
        # put back directory structure in a clean state
        # if keyboard interruption happened at a bad timing
        # while using forced symlink strategy
        if not os.path.exists(current_folder):
            atomic_symlink(a_folder, current_folder)

