class FileExplorerService {

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
        self.loadData = function(query) {
            console.log('Load file list for user ' + query.username + '...')

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
                            "statement": "MATCH (u:User { username:{username} })-[:Created]->(e:Experiment)-[:Composed_By]->(f:File) RETURN {name: f.name}",
                            "parameters": {
                                "username": query.username,
                                "experiment": "MyExp"
                            }
                        }
                    ]
                }
            }).then(self.dataRetrieved);
        }

        // Metodo chiamato una volta ottenute le statistiche sul file dal database. Riorganizzo i dati prima di passarli alla vista
        self.dataRetrieved = function(response) {
            console.log(response);
            console.log('File list successfully retrieved');

             var data = {
                elements: []
            };

            for (var idx = 0; idx < response.data.results[0].data.length; idx++) {

                data.elements.push({
                    name: response.data.results[0].data[idx].row[0].name
                    
                })
            }
            
            return data;
        }
    }

}

export default FileExplorerService;