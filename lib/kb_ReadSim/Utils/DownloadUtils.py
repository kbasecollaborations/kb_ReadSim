import os
from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.VariationUtilClient import VariationUtil


class DownloadUtils:
    def __init__(self, callback_url):
        self.callbackURL = os.environ['SDK_CALLBACK_URL']
        self.au = AssemblyUtil(self.callbackURL)
        self.vu = VariationUtil(self.callbackURL)
        pass

    def download_genome(self, genomeref, output_dir):
        '''
        this funciton downloads genome.
        :param genomeref:
        :param output_dir:
        :return:
        '''

        file = self.au.get_assembly_as_fasta({
          'ref': genomeref,
          'filename': os.path.join(output_dir, "ref_genome.fa")
        })
        return file

    def download_variations(self, variation_ref, filename):
        '''
        This function downloads variations.
        :param variation_ref:
        :param filename:
        :return:
        '''

        filepath = self.vu.get_variation_as_vcf({
            'variation_ref': variation_ref,
            'filename': filename
        })['path']
        return filepath

