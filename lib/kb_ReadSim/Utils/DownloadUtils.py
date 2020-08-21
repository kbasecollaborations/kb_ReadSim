import os
from installed_clients.AssemblyUtilClient import AssemblyUtil


class DownloadUtils:

    def __init__(self, callback_url):
        self.callbackURL = os.environ['SDK_CALLBACK_URL']
        self.au = AssemblyUtil(self.callbackURL)
        pass

    def download_genome(self, genomeref, output_dir):
        file = self.au.get_assembly_as_fasta({
          'ref': genomeref,
          'filename': os.path.join(output_dir, "ref_genome.fa")
        })
        return file
