/*
A KBase module: kb_ReadSim
*/

module kb_ReadSim {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    typedef structure {
        string workspace_name;
        string input_sample_set;
        string strain_info;
        string assembly_or_genome_ref;
        string base_error_rate;
        string outer_distance;
        string standard_deviation;
        string num_read_pairs;
        string len_first_read;
        string len_second_read;
        string mutation_rate;
        string frac_indels;
        string variation_object_name;
        string output_read_object;
    } Inparams;
    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_kb_ReadSim(Inparams params) returns (ReportResults output) authentication required;

   typedef structure {
        string workspace_name;
        string sim_varobject_name;
        string calling_varobject_name;
        string output_var_object;
    } Evalparams;
    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_eval_variantcalling(Evalparams params) returns (ReportResults output) authentication required;
};
