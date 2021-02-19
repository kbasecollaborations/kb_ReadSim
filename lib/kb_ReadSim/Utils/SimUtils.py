from kb_ReadSim.Utils.RunUtils import RunUtils


class SimUtils:
    def __init__(self):
        self.ru = RunUtils()
        pass

    def validate_simreads_params(self, params):
        '''
        Function for validating input parameters
        :param params:
        :return:
        '''

        if 'assembly_or_genome_ref' not in params:
            raise ValueError('required assembly_or_genome_ref field was not defined')
        elif 'base_error_rate' not in params:
            raise ValueError('required base_error_rate field was not defined')
        elif 'outer_distance' not in params:
            raise ValueError('required outer_distance field was not defined')
        elif 'standard_deviation' not in params:
            raise ValueError('required standard_deviation field was not defined')
        elif 'num_read_pairs' not in params:
            raise ValueError('required num_read_pairs field was not defined')
        elif 'len_first_read' not in params:
            raise ValueError('required len_first_read field was not defined')
        elif 'len_second_read' not in params:
            raise ValueError('required len_second_read field was not defined')
        elif 'mutation_rate' not in params:
            raise ValueError('required mutation_rate field was not defined')
        elif 'frac_indels' not in params:
            raise ValueError('required frac_indels field was not defined')
        elif 'variation_object_name' not in params:
            raise ValueError('required variation_object_name field was not defined')
        elif 'output_read_object' not in params:
            raise ValueError('required output_read_object field was not defined')
        elif 'input_sample_set' not in params:
            raise ValueError('required input_sample_set field was not defined')

    def simreads(self, ref_genome, output_fwd_paired_file_path, output_rev_paired_file_path, params):
        '''
        This funciton executes wgsim and generate simulated reads.
        :param ref_genome:
        :param output_fwd_paired_file_path:
        :param output_rev_paired_file_path:
        :param params:
        :return:
        '''

        #Todo : need to add -h as parameter later.

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
          "R" : "A,G",
          "Y" : "C,T",
          "S" : "G,C",
          "W" : "A,T",
          "K" : "G,T",
          "M" : "A,C",
          "B" : "C,G,T",
          "D" : "A,G,T",
          "H" : "A,C,T",
          "V" : "A,C,G",
          "N" : "A,C,G,T"
        }

        try:
            with open(vcf_file, "w") as vcf_out:
                vcf_out.write("##fileformat=VCFv4.3\n")
                vcf_out.write("##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">\n")
                vcf_out.write("##INFO=<ID=DP,Number=1,Type=Integer,Description=\"Total Depth\">\n")
                vcf_out.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tBESC-100\n")

                try:
                    with open(logfile,"r") as vcf_in:
                        for line in vcf_in:
                            line = line.rstrip()
                            rec  = line.split("\t")
                            if(rec[3] in alt_map):
                                alt_list = alt_map[rec[3]].split(",")
                                alt_str = ",".join(list(set(alt_list) - set([rec[2]])))
                                vcf_out.write(rec[0] + "\t" + rec[1] + "\t.\t" + rec[2] + "\t" + alt_str + "\t25\tPASS\tDP=14\tGT\t1/1\n" )
                            else:
                                vcf_out.write(rec[0] + "\t" + rec[1] + "\t.\t" + rec[2] + "\t" + rec[3] + "\t25\tPASS\tDP=14\tGT\t1/1\n")
                except IOError:
                    print ("Error: " + logfile +  " does not appear to exist.")

        except IOError:
            print ("Error: " + vcf_file + " does not appear to exist.")

        return vcf_file 
