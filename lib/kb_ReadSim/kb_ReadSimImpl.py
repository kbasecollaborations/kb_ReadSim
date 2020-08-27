# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import os.path
import uuid
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
        self.su = SimUtils()
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
        self.su.validate_simreads_params(params)

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

        ref_genome = "/kb/module/work/tmp/ref_genome.fa"                #hardcoded for testing
        output_fwd_paired_file_path  = "/kb/module/work/tmp/raed1.fq"   #hardcoded for testing
        output_rev_paired_file_path = "/kb/module/work/tmp/raed2.fq"    #hardcoded for testing

        self.su.simreads(ref_genome, output_fwd_paired_file_path, output_rev_paired_file_path, params)

        retVal = self.ru.upload_reads ({ 'wsname': params['workspace_name'],
                                       'name': params['output_read_object'],
                                       'sequencing_tech': 'illumina',
                                       'fwd_file': output_fwd_paired_file_path,
                                       'rev_file': output_rev_paired_file_path
                                      })

        logfile = "/kb/module/work/tmp/variant.txt"                     #hardcoded for testing
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
                                                'text_message': 'Success'},
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

        print(params)
        self.eu.validate_eval_params(params)

        report_dir = os.path.join(self.shared_folder, str(uuid.uuid4()))
        os.mkdir(report_dir)

        self.ws = Workspace(url=self.ws_url, token=ctx['token'])

        var_object_ref1 = params['varobject1_ref']
        sampleset_ref1 = self.ws.get_objects2({'objects': [{"ref": var_object_ref1, 'included': ['/sample_set_ref']}]})['data'][0]['data']['sample_set_ref']

        var_object_ref2 = params['varobject1_ref']
        sampleset_ref2 = self.ws.get_objects2({'objects': [{"ref": var_object_ref2, 'included': ['/sample_set_ref']}]})['data'][0]['data']['sample_set_ref']

        if(sampleset_ref1 != sampleset_ref2):
            raise Exception("Variation objects are from different sample set\n")

        assembly_ref_set = set()
        genomeset_ref_set = set()

        variation_obj1 = self.ws.get_objects2({'objects': [{'ref': var_object_ref1}]})['data'][0]

        if 'assembly_ref' in variation_obj1['data']:
            assembly_ref1 = variation_obj1['data']['assembly_ref']
            assembly_ref_set.add(assembly_ref1)
        elif 'genome_ref' in variation_obj1['data']:
            genome_ref1 = variation_obj1['data']['genome_ref']
            genomeset_ref_set.add(genome_ref1)

        variation_obj2 = self.ws.get_objects2({'objects': [{'ref': var_object_ref2}]})['data'][0]
        if 'assembly_ref' in variation_obj2['data']:
            assembly_ref2 = variation_obj2['data']['assembly_ref']
            assembly_ref_set.add(assembly_ref2)
        elif 'genome_ref' in variation_obj2['data']:
            genome_ref2 = variation_obj2['data']['genome_ref']
            genomeset_ref_set.add(genome_ref2)

        assembly_or_genome_ref = ''

        if (len(genomeset_ref_set) == 0 and len(assembly_ref_set) != 1):
            raise Exception("variation objects are from different assembly refs")
        elif (len(assembly_ref_set) == 0 and len(genomeset_ref_set) != 1):
            raise Exception("variation objects are from different genome set refs")

        simvarfile = os.path.join(report_dir, "simvarinat.vcf.gz")
        simvarpath = self.du.download_variations(var_object_ref1, simvarfile)
        os.rename(simvarpath, simvarfile)
        self.eu.index_vcf(simvarfile)

        callingvarfile = os.path.join(report_dir, "callingvarinat.vcf.gz")
        callingvarpath = self.du.download_variations(var_object_ref2, callingvarfile)
        os.rename(callingvarpath, callingvarfile)
        self.eu.index_vcf(callingvarfile)

        eval_results = self.eu.variant_evalation(simvarfile, callingvarfile, report_dir)

        unique_vcf1 = eval_results['unique1']
        self.eu.check_path_exists(unique_vcf1)

        unique_vcf2 = eval_results['unique2']
        self.eu.check_path_exists(unique_vcf2)

        common_vcf = eval_results['common']
        self.eu.check_path_exists(common_vcf)

        image_path = self.eu.plot_venn_diagram(report_dir, unique_vcf1, unique_vcf2, common_vcf)
        self.eu.check_path_exists(image_path)

        if(len(assembly_ref_set) != 0):
            assembly_or_genome_ref = assembly_ref_set.pop()
        elif(len(genomeset_ref_set) != 0):
            assembly_or_genome_ref = genomeset_ref_set.pop()

        logging.info("Saving Unique1 vcf\n")
        save_unique_variation_params1 = {'workspace_name': params['workspace_name'],
                                        'genome_or_assembly_ref': assembly_or_genome_ref,
                                        'sample_set_ref': sampleset_ref1,
                                        'sample_attribute_name': 'sample_unique_attr1',
                                        'vcf_staging_file_path': unique_vcf1,
                                        'variation_object_name': params['output_variant_object'] + "_sample1_unique"
        }
        self.vu.save_variation_from_vcf(save_unique_variation_params1)
        logging.info("Saving done\n")

        logging.info("Saving Unique2 vcf\n")
        save_unique_variation_params2 = {'workspace_name': params['workspace_name'],
                                        'genome_or_assembly_ref': assembly_or_genome_ref,
                                        'sample_set_ref': sampleset_ref1,
                                        'sample_attribute_name': 'sample_unique_attr2',
                                        'vcf_staging_file_path': unique_vcf2,
                                        'variation_object_name': params['output_variant_object'] + "_sample2_unique"
        }
        self.vu.save_variation_from_vcf(save_unique_variation_params2)
        logging.info("Saving done\n")

        logging.info("Saving Common vcf\n")
        save_common_variation_params = {'workspace_name': params['workspace_name'],
                                 'genome_or_assembly_ref': assembly_or_genome_ref,
                                 'sample_set_ref': sampleset_ref1,
                                 'sample_attribute_name': 'sample_common_attr',
                                 'vcf_staging_file_path': common_vcf,
                                 'variation_object_name': params['output_variant_object'] + "_sample1_sample2_common"
        }
        self.vu.save_variation_from_vcf(save_common_variation_params)
        logging.info("Saving done\n")

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
