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
            'username': 'lola',
            'experiment': 'lallero',
            'file': $routeParams.filename
        }

        console.log(self.query)

        FileStatisticsService.loadFileStatistics(self.query)
            .then(function(data) {self.processDataForVisualization(data) })
            .catch(function (error) { console.log(error) });

        self.processDataForVisualization = function (data) {
            console.log(data);
            
            self.data = data;

            //self.template = self.config.elements.join("\n");
            //console.log(self.data)
        }

    }

}

export default FileStatisticsController;