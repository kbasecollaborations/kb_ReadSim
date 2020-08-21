import os
import logging
import subprocess
#'from installed_clients.AssemblyUtilClient import AssemblyUtil


class SimUtils:

    def __init__(self, callback_url):
        #self.callbackURL = os.environ['SDK_CALLBACK_URL']
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
        #vcf_file = "/Users/manishkumar/Desktop/apps/kb_ReadSim/test_local/workdir/tmp/log.vcf"
        alt_map = { "A" : "A",
          "C" : "C",
          "G" : "G",
          "T" : "T",
          "R" : "A, G",
          "Y" : "C, T",
          "S" : "G, C",
          "W" : "A, T",
          "K" : "G, T",
          "M" :	"A, C",
          "B" :	"C, G, T",
          "D" :	"A, G, T",
          "H" :	"A, C, T",
          "V" :	"A, C, G",
          "N" :	"A, C, G, T"
        }

        with open(vcf_file, "w") as vcf_out:
             vcf_out.write("##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">\n")
             vcf_out.write("##fileformat=VCFv4.3\n")
             vcf_out.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
             with open(logfile,"r") as vcf_in:
                  for line in vcf_in:
                      line = line.rstrip()
                      rec  = line.strip(" ")
                      if(rec[3] in alt_map):
                         vcf_out.write(rec[0] + "\t" + rec[1] + "\t.\t" + rec[2] + "\t" + alt_map[rec[3]] + "\t25\tPASS\tGT\t1/1\n" )
                      else:
                         vcf_out.write(rec[0] + "\t" + rec[1] + "\t.\t" + rec[2] + "\t" + rec[3] + "\t25\tPASS\tGT\t1/1\n")
        return vcf_file

