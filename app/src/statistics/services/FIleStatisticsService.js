class FileStatisticsService {

    constructor($q, $http, $log) {
        var self = this;

        // Attributi della classe (da Angular)
        self.$q = $q;
        self.$http = $http;
        self.$log = $log;

        // Attributi della classe SPECIFICI
        self.credentials = btoa('neo4j:password');

        // --- Metodi pubblici della classe ---
        
        // Metodo chiamato per ottenere le statistiche sul file calcolate in fare di inserimento dei dati nel database
        self.loadFileStatistics = function(query) {
            console.log('Load file informations for ' + query.file.split('.vcf')[0] + '...')

            return $http({
                method: 'POST',
                url: 'http://localhost:7474/db/data/transaction/commit',
                headers: {
                    'Authorization': 'Basic ' + self.credentials,
                    'Content-Type': 'Application/json',
                    'Accepts': 'Application/json',
                    'X-Stream': 'true'
                },
                data: {
                    "statements": [
                        {
                            "statement": "match(f: File { name: {filename} }) return f as statistics",
                            "parameters": {
                                "filename": query.file
                            }
                        }
                    ]
                }
            }).then(self.statisticsRetrieved);
        }

        // Metodo chiamato una volta ottenute le statistiche sul file dal database. Riorganizzo i dati prima di passarli alla vista
        self.statisticsRetrieved = function(response) {
            console.log('Statistics successfully retrieved');

            return response.data.results[0].data[0].row[0];
        }
    }

}

export default FileStatisticsService;