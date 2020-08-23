# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import uuid
import shutil
from kb_ReadSim.Utils.DownloadUtils import DownloadUtils
from kb_ReadSim.Utils.SimUtils import SimUtils
from kb_ReadSim.Utils.VcfEvalUtils import VcfEvalUtils
from kb_ReadSim.Utils.htmlreportutils import htmlreportutils
from installed_clients.readsUtilsClient import ReadsUtils
from installed_clients.VariationUtilClient import VariationUtil
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.WorkspaceClient import Workspace

#END_HEADER


class kb_ReadSim:
    '''
    Module Name:
    kb_ReadSim

    Module Description:
    A KBase module: kb_ReadSim
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/kbasecollaborations/kb_ReadSim.git"
    GIT_COMMIT_HASH = "c9c0185e34d25be57cc6e1c901d8801fbc0f4784"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        self.du = DownloadUtils(self.callback_url)
        self.su = SimUtils(self.callback_url)
        self.ru = ReadsUtils(self.callback_url)
        self.vu = VariationUtil(self.callback_url)
        self.eu = VcfEvalUtils()
        self.hu = htmlreportutils()
        self.ws_url = config['workspace-url']
        self.wsc = Workspace(self.ws_url)
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_kb_ReadSim(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of type "Inparams" -> structure: parameter
           "workspace_name" of String, parameter "input_sample_set" of
           String, parameter "strain_info" of String, parameter
           "assembly_or_genome_ref" of String, parameter "base_error_rate" of
           String, parameter "outer_distance" of String, parameter
           "standard_deviation" of String, parameter "num_read_pairs" of
           String, parameter "len_first_read" of String, parameter
           "len_second_read" of String, parameter "mutation_rate" of String,
           parameter "frac_indels" of String, parameter
           "variation_object_name" of String, parameter "output_read_object"
           of String
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_kb_ReadSim
        output_dir = self.shared_folder
        print(params)
        genomeref = params['assembly_or_genome_ref']

        genome_or_assembly_ref = params['assembly_or_genome_ref']
        obj_type = self.wsc.get_object_info3({
            'objects':[{
                'ref': genome_or_assembly_ref
                      }]})['infos'][0][2]
        if ('KBaseGenomes.Genome' in obj_type):
            genome_ref = genome_or_assembly_ref
            subset = self.wsc.get_object_subset([{
                    'included': ['/assembly_ref'],
                    'ref': genome_ref
                }])
            assembly_ref = subset[0]['data']['assembly_ref']
        elif ('KBaseGenomeAnnotations.Assembly' in obj_type):
            assembly_ref = genome_or_assembly_ref
        else:
            raise ValueError(obj_type + ' is not the right input for this method. '
                                      + 'Valid input include KBaseGenomes.Genome or '
                                      + 'KBaseGenomeAnnotations.Assembly ')

        self.du.download_genome(assembly_ref, output_dir)

        ref_genome = "/kb/module/work/tmp/ref_genome.fa"
        output_fwd_paired_file_path  = "/kb/module/work/tmp/raed1.fq"
        output_rev_paired_file_path = "/kb/module/work/tmp/raed2.fq"
        self.su.simreads(ref_genome, output_fwd_paired_file_path, output_rev_paired_file_path, params)


        retVal = self.ru.upload_reads ({ 'wsname': params['workspace_name'],
                                       'name': params['output_read_object'],
                                       'sequencing_tech': 'illumina',
                                       'fwd_file': output_fwd_paired_file_path,
                                       'rev_file': output_rev_paired_file_path
                                      })

        logfile = "/kb/module/work/tmp/variant.txt"
        vcf_file = self.su.format_vcf(logfile)
        save_variation_params = {'workspace_name': params['workspace_name'],
            'genome_or_assembly_ref': params['assembly_or_genome_ref'],      
            'sample_set_ref':params['input_sample_set'],
            'sample_attribute_name':'sample_attr',
            'vcf_staging_file_path': vcf_file,
            'variation_object_name': params['variation_object_name']
            } 
        self.vu.save_variation_from_vcf(save_variation_params)

        report = KBaseReport(self.callback_url)
        report_info = report.create({'report': {'objects_created':[],
                                                'text_message': params['parameter_1']},
                                                'workspace_name': params['workspace_name']})
        output = {
            'report_name': report_info['name'],
            'report_ref': report_info['ref'],
        }
        #END run_kb_ReadSim

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_kb_ReadSim return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def run_eval_variantcalling(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of type "Evalparams" -> structure: parameter
           "workspace_name" of String, parameter "sim_varobject_name" of
           String, parameter "calling_varobject_name" of String, parameter
           "output_var_object" of String
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_eval_variantcalling

        #output_dir = os.path.join(self.shared_folder, str(uuid.uuid4()))
        report_dir = os.path.join(self.shared_folder, str(uuid.uuid4()))
        os.mkdir(report_dir)

        #output_dir = self.shared_folder

        simvarfile = os.path.join(report_dir, "simvarinat.vcf.gz")

        simvarpath = self.vu.get_variation_as_vcf({
                'variation_ref': params['varobject1_ref'],
                'filename': simvarfile
            })['path']
        os.rename(simvarpath, simvarfile)  # for debugging
        #shutil.copyfile(simvarpath, simvarfile)
        self.eu.index_vcf(simvarfile)

        callingvarfile = os.path.join(report_dir, "callingvarinat.vcf.gz")
        callingvarpath = self.vu.get_variation_as_vcf({
                'variation_ref': params['varobject2_ref'],
                'filename': callingvarfile
            })['path']

        #shutil.copyfile(callingvarpath, callingvarfile)
        os.rename(callingvarpath, callingvarfile)  #for deubugging
        self.eu.index_vcf(callingvarfile)

        self.eu.variant_evalation(simvarfile, callingvarfile, report_dir)

        self.eu.plot_venn_diagram(report_dir)

        report = KBaseReport(self.callback_url)
        report_info = report.create({'report': {'objects_created': [],
                                                'text_message': 'Success'},
                                     'workspace_name': params['workspace_name']})
        workspace = params['workspace_name']
        output = self.hu.create_html_report(self.callback_url, report_dir, workspace)
        #END run_eval_variantcalling

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_eval_variantcalling return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
