import uuid
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.KBaseReportClient import KBaseReport

class htmlreportutils:
    def __init__(self):
        pass

    def import_image(self, output_dir):
        '''
        function for adding venn_diagram to report
        :param output_dir:
        :return: image path
        '''

        output = "<html><head></head><body>"
        output += "<h2>Vein Diagram</h2>"
        output += "<img src=venn_diagram.png width=\"800\" height=\"600\">"
        output += "</body></html>"
        return output

    def create_html_report(self, callback_url, output_dir, workspace_name):
        '''
        function for creating html report
        :param callback_url:
        :param output_dir:
        :param workspace_name:
        :return: report
        '''

        dfu = DataFileUtil(callback_url)
        report_name = 'kb_variant_report_' + str(uuid.uuid4())
        report = KBaseReport(callback_url)
        index_file_path = "./venn_diagram.png"
        htmlstring = self.import_image(output_dir)

        try:
            with open(output_dir +"/index.html" , "w") as html_file:
               html_file.write(htmlstring +"\n")
        except IOError:
            print("Unable to write "+ index_file_path + " file on disk.")

        report_shock_id = dfu.file_to_shock({'file_path': output_dir,
                                            'pack': 'zip'})['shock_id']

        html_file = {
            'shock_id': report_shock_id,
            'name': 'index.html',
            'label': 'index.html',
            'description': 'HTMLL report for Variation Comparision'
            }
        
        report_info = report.create_extended_report({
                        'direct_html_link_index': 0,
                        'html_links': [html_file],
                        'report_object_name': report_name,
                        'workspace_name': workspace_name
                    })
        return {
            'report_name': report_info['name'],
            'report_ref': report_info['ref']
        }


