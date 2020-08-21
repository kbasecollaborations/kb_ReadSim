import os
import logging
import subprocess
from installed_clients.AssemblyUtilClient import AssemblyUtil


class SimUtils:

    def __init__(self, callback_url):
        self.callbackURL = os.environ['SDK_CALLBACK_URL']
        pass

    def run_cmd(self, cmd):
        """
        This function runs a third party command line tool
        eg. bgzip etc.
        :param command: command to be run
        :return: success
        """
        command = " ".join(cmd)
        print(command)
        logging.info("Running command " + command)
        cmdProcess = subprocess.Popen(command,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT,
                                      shell=True)
        for line in cmdProcess.stdout:
            logging.info(line.decode("utf-8").rstrip())
            cmdProcess.wait()
            logging.info('return code: ' + str(cmdProcess.returncode))
            if cmdProcess.returncode != 0:
                raise ValueError('Error in running command with return code: '
                                 + command
                                 + str(cmdProcess.returncode) + '\n')
        logging.info("command " + command + " ran successfully")
        return "success"

    def simreads(self, ref_genome, output_fwd_paired_file_path, output_rev_paired_file_path, params):
        cmd = ["/kb/module/deps/wgsim/wgsim"]
        cmd.extend(["-e", params['base_error_rate']])
        cmd.extend(["-d", params['outer_distance']])
        cmd.extend(["-s", params['standard_deviation']])
        cmd.extend(["-N", params['num_read_pairs']])
        cmd.extend(["-1", params['len_first_read']])
        cmd.extend(["-2", params['len_second_read']])
        cmd.extend(["-r", params['mutation_rate']])
        cmd.extend(["-R", params['frac_indels']]) 
        cmd.append(ref_genome)
        cmd.append(output_fwd_paired_file_path)
        cmd.append(output_rev_paired_file_path)
        cmd.extend([">", "/kb/module/work/tmp/variant.txt"])
        self.run_cmd(cmd)

    def format_vcf(self, logfile):
        vcf_file = "/kb/module/work/tmp/log.vcf"
        '''
        A	Adenine
C	Cytosine
G	Guanine
T (or U)	Thymine (or Uracil)
R	A or G
Y	C or T
S	G or C
W	A or T
K	G or T
M	A or C
B	C or G or T
D	A or G or T
H	A or C or T
V	A or C or G
N	any base
. or -	gap
        '''

        #fastacmd -d sequences.fa -s Chr01 -L 2,10q
        return vcf_file
