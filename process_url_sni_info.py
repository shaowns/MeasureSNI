from csv import reader
from argparse import ArgumentParser
from mysql.connector import Error
from subprocess import check_output as co
from timeit import default_timer as timer
import logging
import imp
import mysql_dac as md


def setup_logging():
    """
    Setup a reusable logger
    """
    logger = logging.getLogger('url_data')
    hdlr = logging.FileHandler('./logs/url_data.log', mode='w')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    return logger


def get_cmd_output(command):
    """
    Run the complex (piped command) in shell (requires UNIX shell) and return the output.
    """
    cstr = co(command, shell=True)
    return cstr


def process_url(url):
    """
    Process the certificate extraction and checks if any of the SNI criteria is met.
    """
    default_cert_cmd = "echo | openssl s_client -connect {}:443 2>&1 | sed -n '/BEGIN CERTIFICATE/,/END CERTIFICATE/p'".format(url)
    sni_cert_cmd = "echo | openssl s_client -connect {}:443 -servername {} 2>&1 | sed -n '/BEGIN CERTIFICATE/,/END CERTIFICATE/p'".format(url, url)

    default_cert_str = get_cmd_output(default_cert_cmd)
    sni_cert_str = get_cmd_output(sni_cert_cmd)

    support_sni = False
    requires_sni = False
    force_sni = False

    if sni_cert_str:
        support_sni = True

    if default_cert_str != sni_cert_str:
        requires_sni = True

    if not default_cert_str and sni_cert_str:
        force_sni = True

    return support_sni, requires_sni, force_sni, default_cert_str, sni_cert_str


def store_url_data(rank, url, logger):
    """
    Stores the url certificate data into MySql table (add the configurations into the .ini file).
    """
    try:
        support_sni, requires_sni, force_sni, default_cert, sni_cert = process_url(url)
        sp_args = []
        sp_args.append(rank)
        sp_args.append(url)
        sp_args.append(support_sni)
        sp_args.append(requires_sni)
        sp_args.append(force_sni)
        sp_args.append(default_cert)
        sp_args.append(sni_cert)
        sp_args.append(0)

        insert_id = md.call_procedure('add_url_data', sp_args)
        return insert_id

    except Error as err:
        logger.error("DB insertion error, url: " + url + ", Exception: " + str(err))
    except Exception as e:
        logger.error("URL cert data command failed, url: " + url + ", Exception: " + str(e))

    return -1


def get_url_iterator(filename, sidx):
    """
    Read the url from the large csv file starting at given index without loading the file into memory.
    """
    with open(filename, "rb") as f:
        dr = reader(f)
        for idx, row in enumerate(dr):
            if idx < sidx:
                continue
            yield row


def do_stuff(filename, logger, sidx=0):
    """
    Start running the url processing starting at given row index.
    """
    count = 0
    for row in get_url_iterator(filename, sidx):
        rank, url = row
        rid = store_url_data(rank, url, logger)
        if rid != -1:
            count += 1

    return count


def main():
    """
    Main function, entry point of script. Handles command line arguments.
    """
    ap = ArgumentParser(description='Use the script to pull the certificate data of the urls in the csv file.')
    ap.add_argument('-f', '-file', help='CSV file containing urls at column 1, rank at column 0', required=True)
    ap.add_argument('-i', '-idx', help='Starting index of the csv file', required=False, default=0)

    # Reload the dac for changes.
    imp.reload(md)

    # Set up logger, will clear everything in logging file.
    logger = setup_logging()

    # Let it rip.
    args = ap.parse_args()
    filename = args.f
    sidx = int(args.i)

    start = timer()
    count = do_stuff(filename, logger, sidx)
    end = timer()
    elapsed = end - start

    print "Processed {} URLs in {} seconds".format(count, elapsed)
    return


if __name__ == "__main__":
    main()
