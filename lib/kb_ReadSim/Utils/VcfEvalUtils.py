import os
import os.path
from os import path
import subprocess
import matplotlib.pyplot as plt
from matplotlib_venn import venn2
from kb_ReadSim.Utils.RunUtils import RunUtils

class VcfEvalUtils:
    def __init__(self):
        self.ru = RunUtils()
        pass

    def validate_eval_params(self, params):
        '''
        Function for validating input parameters
        :param params:
        :return:
        '''

        if 'varobject_ref1' not in params:
            raise ValueError('required varobject_ref1 field was not defined')
        elif 'varobject_ref2' not in params:
            raise ValueError('required varobject_ref2 field was not defined')
        elif 'output_variant_object' not in params:
            raise ValueError('required output_variant_object field was not defined')

    def bgzip_vcf(self, vcf_file):
        '''
        This function zip (bgzip) vcf file
        :param vcf_file:
        :return: bgzipped vcf file
        '''

        bgzip_cmd = ["bgzip"]
        bgzip_cmd.extend(["-c", vcf_file])
        outfile = vcf_file + ".gz"
        bgzip_cmd.extend([">", outfile])
        self.ru.run_cmd(bgzip_cmd)
        return outfile

    def index_vcf(self, vcf_file):
        '''
        This function index the bzipped vcf file.
        :param vcf_file:
        :return:
        '''

        index_cmd = ["tabix"]
        index_cmd.extend(["-p", "vcf" ])
        index_cmd.append(vcf_file)
        self.ru.run_cmd(index_cmd)

    def variant_evalation(self, simvar_file, callig_varfile, output_dir):
        '''
        funciton for evaluating varinats generated from variant calling pipeline
        :param simvar_file:
        :param callig_varfile:
        :param output_dir:
        :return: eval_results
        '''

        cmd = ["bcftools", "isec"]
        cmd.append(simvar_file)
        cmd.append(callig_varfile)
        cmd.extend(["-p", output_dir])
        self.ru.run_cmd(cmd)

        unique_vcf1 = os.path.join(output_dir, '0000.vcf')
        unique_vcf2 = os.path.join(output_dir, '0001.vcf')
        common_vcf = os.path.join(output_dir, "0002.vcf")

        eval_results = { "common" : common_vcf,
                        "unique1": unique_vcf1,
                        "unique2": unique_vcf2
        }

        return eval_results

    def check_path_exists(self, file):
        if (not path.exists(file)):
            raise Exception(file  + "does not exist")

    def plot_venn_diagram(self, output_dir, unique_file1, unique_file2, common_file):
        '''
        funciotn for plotting venn diagram
        :param output_dir:
        :return: venn-diagram image file path
        '''

        unique1 = subprocess.check_output("cat " + unique_file1 + " | grep -v -c '#' | awk '{print $1}'", shell=True)
        unique2 = subprocess.check_output("cat " + unique_file2 + " | grep -v -c '#' | awk '{print $1}'", shell=True)
        common = subprocess.check_output("cat " + common_file + " | grep -v -c '#' | awk '{print $1}'", shell=True)

        A = int(unique1.rstrip())
        B = int(unique2.rstrip())
        AB = int(common.rstrip())

        venn2(subsets=(A, B, AB), set_labels=('Variation 1', 'Variation 2'))
        image_path = os.path.join(output_dir, 'venn_diagram.png')
        plt.savefig(image_path)

        return image_path

