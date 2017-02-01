import os, time

def is_locked(filepath):
    """Checks if a file is locked by opening it in append mode.
    If no exception thrown, then the file is not locked.
    """
    locked = None
    file_object = None
    if os.path.exists(filepath):
        try:
            #print "Trying to open %s." % filepath
            buffer_size = 8
            # Opening file in append mode and read the first 8 characters.
            file_object = open(filepath, 'a', buffer_size)
            if file_object:
                #print "%s is not locked." % filepath
                locked = False
        except IOError, message:
            #print "File is locked (unable to open in append mode). %s." % message
            locked = True
        finally:
            if file_object:
                file_object.close()
                #print "%s closed." % filepath
    else:
        print "%s not found." % filepath
    return locked

def wait_for_files(filepaths):
    """Checks if the files are ready.

    For a file to be ready it must exist and can be opened in append
    mode.
    """
    wait_time = 5
    for filepath in filepaths:
        # If the file doesn't exist, wait wait_time seconds and try again
        # until it's found.
        while not os.path.exists(filepath):
            print "%s hasn't arrived. Waiting %s seconds." % \
                  (filepath, wait_time)
            time.sleep(wait_time)
        # If the file exists but locked, wait wait_time seconds and check
        # again until it's no longer locked by another process.
        while is_locked(filepath):
            print "%s is currently in use. Waiting %s seconds." % \
                  (filepath, wait_time)
            time.sleep(wait_time)

# Test
if __name__ == '__main__':
    files = [r"C:\testfolder\testfile1.txt",
             r"C:\testfolder\testfile2.txt"]
    print "wait_for_files(files)<br>"