import config from "configuration.json!json";

class FileStatisticsService {

    constructor($q, $http, $log) {
        var self = this;

        // Attributi della classe (da Angular)
        self.$q = $q;
        self.$http = $http;
        self.$log = $log;

        // Attributi della classe SPECIFICI
        self.credentials = btoa(config.neo4j.username + ':' + config.neo4j.password);

        // --- Metodi pubblici della classe ---

        // Metodo chiamato per ottenere le statistiche sul file calcolate in fare di inserimento dei dati nel database
        self.loadFileStatistics = function (query) {
            console.log('Load file informations for ' + query.file.split('.vcf')[0] + '...')

        //return $http.get("http://" + config.django.address + ":" + config.django.port + "/dataService/" + query.username + "/" + query.experiment + "/" + query.file + "/statistics/")
        //    .then(self.statisticsRetrieved);
        

           return $http({
                method: 'POST',
                url: 'http://' + config.neo4j.address + ':' + config.neo4j.port + '/db/data/transaction/commit',
                headers: {
                    'Authorization': 'Basic ' + self.credentials,
                    'Content-Type': 'Application/json',
                    'Accepts': 'Application/json',
                    'X-Stream': 'true'
                },
                data: {
                    "statements": [
                        {
                            "statement": "MATCH (u:User {username: {username}})-[:Created]->(e:Experiment {name: {experiment} })-[:Composed_By]->(f:File { name:{filename} }) RETURN f.statistics as statistics",
                            "parameters": {
                                "username": "lola",
                                "experiment": query.experiment,
                                "filename": query.file
                            }
                        }
                    ]
                }
            }).then(self.statisticsRetrieved);
       }

        // Metodo chiamato una volta ottenute le statistiche sul file dal database. Riorganizzo i dati prima di passarli alla vista
        self.statisticsRetrieved = function (response) {
            console.log('Statistics successfully retrieved');
            return response.data.results[0].data[0].row[0];
            //return response.data;
        }
    }

}

export default FileStatisticsService;