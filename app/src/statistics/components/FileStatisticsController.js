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
            'experiment': $routeParams.experiment,
            'file': $routeParams.filename
        }

        console.log(self.query)

        FileStatisticsService.loadFileStatistics(self.query).then(self.processDataForVisualization).catch(function (error) { console.log(error) });

        self.processDataForVisualization = function (data) {
            self.data = data;

            self.template = self.config.row.join("\n");
            console.log(self.data)
        }

    }

}

export default FileStatisticsController;