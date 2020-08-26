import logging
import subprocess
from kb_ReadSim.Utils.RunUtils import RunUtils


class SimUtils:
    def __init__(self):
        self.ru = RunUtils()
        pass

    def simreads(self, ref_genome, output_fwd_paired_file_path, output_rev_paired_file_path, params):
        '''
        This funciton executes wgsim and generate simulated reads.
        :param ref_genome:
        :param output_fwd_paired_file_path:
        :param output_rev_paired_file_path:
        :param params:
        :return:
        '''
        cmd = ["/kb/module/deps/wgsim/wgsim"]
        cmd.extend(["-e", str(params['base_error_rate'])])
        cmd.extend(["-d", str(params['outer_distance'])])
        cmd.extend(["-s", str(params['standard_deviation'])])
        cmd.extend(["-N", str(params['num_read_pairs'])])
        cmd.extend(["-1", str(params['len_first_read'])])
        cmd.extend(["-2", str(params['len_second_read'])])
        cmd.extend(["-r", str(params['mutation_rate'])])
        cmd.extend(["-R", str(params['frac_indels'])])
        cmd.append(ref_genome)
        cmd.append(output_fwd_paired_file_path)
        cmd.append(output_rev_paired_file_path)
        cmd.extend([">", "/kb/module/work/tmp/variant.txt"])
        self.ru.run_cmd(cmd)

    def format_vcf(self, logfile):
        '''
        This function converrt log file generated from wgsim into vcf format.
        :param logfile:
        :return: vcf log file
        '''
        vcf_file = "/kb/module/work/tmp/log.vcf"     #Hardcoded path

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

        try:
            with open(vcf_file, "w") as vcf_out:
                vcf_out.write("##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">\n")
                vcf_out.write("##INFO=<ID=DP,Number=1,Type=Integer,Description=\"Total Depth\">")
                vcf_out.write("##fileformat=VCFv4.3\n")
                vcf_out.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tBESC-100\n")

                try:
                    with open(logfile,"r") as vcf_in:
                        for line in vcf_in:
                            line = line.rstrip()
                            rec  = line.split("\t")
                            if(rec[3] in alt_map):
                                vcf_out.write(rec[0] + "\t" + rec[1] + "\t.\t" + rec[2] + "\t" + alt_map[rec[3]] + "\t25\tPASS\tDP=14\tGT\t1/1\n" )
                            else:
                                vcf_out.write(rec[0] + "\t" + rec[1] + "\t.\t" + rec[2] + "\t" + rec[3] + "\t25\tPASS\tDP=14\tGT\t1/1\n")
                except IOError:
                    print ("Error: " + logfile +  " does not appear to exist.")

        except IOError:
            print ("Error: " + vcf_file + " does not appear to exist.")

        return vcf_file

