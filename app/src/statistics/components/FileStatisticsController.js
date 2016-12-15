import config from "src/statistics/config/vcf.config.json!json";

class FileStatisticsController {

    /** Costruttore
     * 
     * @param $log
     */
    constructor($http, $routeParams, $log, FileStatisticsService) {
        var self = this;
        self.$log = $log;

        self.config = config;

        self.query = {
            'file': $routeParams.filename
        }



        FileStatisticsService.loadFileStatistics(self.query).then(function (data) {
            console.log(data);
            self.data = data;

        }).catch(function () { console.log('Some error occurred') });

        self.processDataForVisualization = function (data) {
            self.data = data;

            self.template = self.config.row.join("\n");
            console.log(self.data)
        }

    }

}

export default FileStatisticsController;