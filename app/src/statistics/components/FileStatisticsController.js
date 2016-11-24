class FileStatisticsController {

    /** Costruttore
     * 
     * @param $log
     */
    constructor($http, $log, FileStatisticsService) {
        var self = this;
        self.$log = $log;

        self.config = {};

        self.query = {
            'file': 'U11_80M_R2.annotated.hg19_multianno.vcf'
        }

        // Caricamento del file di config
        $http.get('src/statistics/config/vcf.config.json')
            .then(

            function (response) {
                console.log("Loaded configuration file");
                self.config = response.data;

                console.log(self.config);
            },

            function (error) {
                console.log("Some error occurred");
            }

            );


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