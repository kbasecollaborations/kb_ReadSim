import os
import logging
import subprocess
import matplotlib.pyplot as plt
from matplotlib_venn import venn2

class VcfEvalUtils:

    def __init__(self):
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

    def bgzip_vcf(self, vcf_file):
        bgzip_cmd = ["bgzip"]
        bgzip_cmd.extend(["-c", vcf_file])
        outfile = vcf_file + ".gz"
        bgzip_cmd.extend([">", outfile])
        self.run_cmd(bgzip_cmd)
        return outfile

    def index_vcf(self, vcf_file):
        index_cmd = ["tabix"]
        index_cmd.extend(["-p", "vcf" ])
        index_cmd.append(vcf_file)
        self.run_cmd(index_cmd)

    def variant_evalation(self, simvar_file, callig_varfile, output_dir):
        cmd = ["bcftools", "isec"]
        cmd.append(simvar_file)
        cmd.append(callig_varfile)
        cmd.extend(["-p", output_dir])
        self.run_cmd(cmd)

    def plot_venn_diagram(self, output_dir):
        unique1 = subprocess.check_output("cat " + os.path.join(output_dir, '0000.vcf') + " | grep -v -c '#' | awk '{print $1}'", shell=True)
        unique2 = subprocess.check_output("cat " + os.path.join(output_dir, '0001.vcf') + " | grep -v -c '#' | awk '{print $1}'", shell=True)
        common = subprocess.check_output("cat " + os.path.join(output_dir, '0002.vcf') + " | grep -v -c '#' | awk '{print $1}'", shell=True)
        A = int(unique1.rstrip())
        B =int(unique2.rstrip())
        AB = int(common.rstrip())

        venn2(subsets=(AB, A, B), set_labels=('Simulated Variants', 'Calling Variants'))
        plt.savefig(os.path.join(output_dir, 'venn_diagram.png'))

#ve = VcfEvalUtils()
#ve.varian_evalation("gatk_variation.fixedheader.vcf.gz", "jmc2_test.vcf.gz", "/Users/manishkumar/Desktop/apps/kb_ReadSim/lib/kb_ReadSim/Utils")
#ve.plot_venn_diagram("/Users/manishkumar/Desktop/apps/kb_ReadSim/lib/kb_ReadSim/Utils")

