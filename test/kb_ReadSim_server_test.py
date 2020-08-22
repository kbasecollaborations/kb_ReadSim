# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser

from kb_ReadSim.kb_ReadSimImpl import kb_ReadSim
from kb_ReadSim.kb_ReadSimServer import MethodContext
from kb_ReadSim.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace


class kb_ReadSimTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kb_ReadSim'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'kb_ReadSim',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = kb_ReadSim(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        suffix = int(time.time() * 1000)
        cls.wsName = "test_ContigFilter_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': cls.wsName})  # noqa

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_your_method(self):
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})
        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
        ret = self.serviceImpl.run_kb_ReadSim(self.ctx, {'workspace_name': 'pranjan77:narrative_1596711680507',
                                                         'assembly_or_genome_ref':'52890/66/1',
                                                         'base_error_rate':'0.02',
                                                         'outer_distance':'500',
                                                         'standard_deviation':'50',
                                                         'num_read_pairs':'1000000',
                                                         'len_first_read':'70',
                                                         'len_second_read':'70',
                                                         'mutation_rate':'0.001',
                                                         'frac_indels':'0.15',
                                                         'variation_object_name':'output_var_obj',
                                                         'output_read_object':'output_read_object',
                                                         'input_sample_set':'52890/11/1',
                                                         'parameter_1': 'Success'
                                                        })
    '''
    def test_run_eval_variantcalling(self):
        ret = self.serviceImpl.run_eval_variantcalling(self.ctx, {'workspace_name': 'pranjan77:narrative_1596711680507',
                                                         'varobject1_ref': '52890/45/1',
                                                         'varobject2_ref': '52890/42/1',
                                                         'output_variant_object':'output_variant_object'
                                                        })
    '''
