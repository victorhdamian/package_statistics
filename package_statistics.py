# #######################################################
# package_statistics.py
# This cli tool takes the debian package architecture
# (amd64, mips etc.) as an argument and returns
# the statistics of the top 10 packages that have the
# most files associated with them
# #######################################################

import sys
import urllib2
import gzip
import collections
from collections import OrderedDict
from itertools import islice

# #######################################################
# download:
# downloads the compressed Contents file associated with
# the debian package architecture from a Debian mirror
#
# #######################################################
def download(download_url, mirror_url):
    file_name = download_url.split('/')[-1]
    u = urllib2.urlopen(download_url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)
    print ("from " + mirror_url)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,
    print (file_name + " Download complete")
    f.close()

# #######################################################
# gunzip:
# unzips the compressed Contents file associated with
# the debian package architecture downloaded from a
# Debian mirror

# #######################################################
def gunzip(source_file,dest_file):
    input = gzip.GzipFile(source_file, 'rb')
    s = input.read()
    input.close()

    output = open(dest_file, 'wb')
    output.write(s)
    print(source_file + " Uncompress complete")
    output.close()

# #######################################################
# pars:
# parses the file to output the statistics of the top 10
# packages that have the most files associated with them
#
# #######################################################
def pars(filepath):
    try:
        result = collections.defaultdict(list)
        with open(filepath,"r") as f:
            for line in f:
                value, key = line.split(' ', 1)
                if key in result:
                    result[key].append(value)
                else:
                    result[key] = [value]
        result = OrderedDict(sorted(result.items(), key=lambda (k,v):len(v), reverse=True))
        return result
    finally:
        f.close()

def take(n, iterable):
    return list(islice(iterable, n))


def main():
    # sets mirror url
    mirror_url = 'http://ftp.uk.debian.org/debian/dists/stable/main/'
    # sets architecture compressed contents file url
    contents_file = "Contents-" + sys.argv[1] + ".gz"
    # sets uncompress contents file path
    destination_file = contents_file.split('.', 1)[0]
    # sets download url
    download_url = mirror_url + contents_file
    download(download_url,mirror_url)
    gunzip(contents_file,destination_file)
    output = pars(destination_file)

    # print the statistics of the top 10
    # packages that have the most files associated with them
    ten_items = take(10, output.iteritems())
    count = 0
    for key, value in ten_items:
        count += 1
        print(count, key, len(filter(bool, value)))

if __name__ == "__main__":
    main()