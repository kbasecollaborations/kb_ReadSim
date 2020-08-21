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
        string variation_object_name;
        string output_read_object;
    } Inparams;
    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_kb_ReadSim(Inparams params) returns (ReportResults output) authentication required;

};
