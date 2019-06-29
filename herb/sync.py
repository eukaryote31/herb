import os
import shutil

from herb.traversal import rel_path_of, traverse
from herb.metadata import Session, file_latest, transaction_scope, add_file, outdated_files
from herb.models import File


def remove_outdated(dest, dev_uuid):
    session = Session()
    with transaction_scope(session) as sess:
        outdated_files()


def copy_tree(src, dest, dev_uuid):
    session = Session()
    total_updated = 0
    for srcf in traverse(src):

        with transaction_scope(session) as sess:

            # is stored version out of date?
            relpath = rel_path_of(src, srcf)
            destf = os.path.join(dest, relpath)

            if os.path.islink(srcf):
                shutil.copy2(srcf, destf, follow_symlinks=False)
                total_updated += 1
                continue
            elif os.path.isdir(srcf):
                if os.path.exists(destf) and os.stat(destf).st_mtime > os.stat(srcf).st_mtime:
                    continue
                try:
                    # TODO: somehow make sure parent directory doesn't get modification time updated
                    os.mkdir(destf)
                except FileExistsError:
                    pass

                shutil.copystat(srcf, destf)
                total_updated += 1
                continue

            statbuf = os.stat(srcf)

            # must be checked each time because filesystem may have padding, compression, etc.
            total, used, free = shutil.disk_usage(dest)

            # TODO: move to central config
            # this is the number of bytes to reserve for metadata, etc; breathing room
            if statbuf.st_size > free - 4 * 1024 * 1024 * 1024:
                # TODO: deal with massive files gracefully
                return

            latest_stored = file_latest(sess, relpath)

            if latest_stored is None or latest_stored.last_modified < statbuf.st_mtime:
                # copy preserving attributes
                # TODO: somehow make sure parent directory doesn't get modification time updated
                shutil.copy2(srcf, destf, follow_symlinks=False)

                newfile = File(path=relpath, last_modified=statbuf.st_mtime, device_id=dev_uuid, size=statbuf.st_size)
                add_file(sess, newfile)
                print(relpath)

                total_updated += 1

    return {'updated': total_updated}
