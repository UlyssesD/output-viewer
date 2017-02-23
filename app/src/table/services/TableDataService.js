import config from "configuration.json!json";

class TableDataService {

    constructor($q, $http, $log) {

        var self = this;

        // Attributi della classe (da Angular)
        self.$q = $q;
        self.$http = $http;
        self.$log = $log;

        // Attributi della classe SPECIFICI
        self.credentials = btoa(config.neo4j.username + ':' + config.neo4j.password);

        // --- Metodi pubblici della classe ---

        // Interrogo il database per ottenere le varianti secondo la query passata in input
        self.loadVariantsFromQuery = function(query) {
            console.log('Retrieving data for selected query...');

            return $http.get("http://localhost:8000/dataService/" + query.username + "/" + query.experiment + "/" + query.file + "/details/?page=" + query.page + "&limit=" + query.limit, {
                'params': {
                    "filters": query.filters
                } 
            })
            .then(self.variantRetrieved);

/*
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
                            "statement": [
                                "MATCH (u:User {username: {username}})-[:Created]->(e:Experiment)-[:Composed_By]->(f:File {name:{filename}}) WITH f",
                                "MATCH (f)-[:Contains]->(i:Info) WITH f, count(i) as total",
                                "MATCH (f)-[:Contains]->(i:Info) WITH  total, i ORDER BY i.info_id SKIP {skip} LIMIT {limit}",
                                "MATCH (i)-[fv:For_Variant]->(v:Variant) WITH  total, i, v, fv",
                                "MATCH (i)-[sb:Supported_By]->(g:Genotype) WITH total, i, v, fv, collect({sample: g, attr: sb}) as genotypes",
                                "RETURN {total: total, variant: {common: v, attr: fv}, annotations: i, genotypes: genotypes }"
                            ].join(" "),
                            "parameters": {
                                "username": query.username,
                                "experiment": "MyExp",
                                "filename": query.file,
                                "skip": query.skip,
                                "limit": query.limit
                            }
                        }

                    ]
                }
            }).then(self.variantRetrieved);
            */

        };

        // Metodo chiamato una volta ottenute le varianti dal database. Riorganizzo i dati prima di passarli alla vista
        self.variantRetrieved = function(response) {
            console.log('Data successfully retrieved');
            console.log(response);

/*
            var data = {
                count: 0,
                elements: []
            };

            data.count = response.data.results[0].data[0].row[0].total;

            for (var idx = 0; idx < response.data.results[0].data.length; idx++) {

                data.elements.push({
                    variant: response.data.results[0].data[idx].row[0].variant,
                    annotations: response.data.results[0].data[idx].row[0].annotations,
                    genotypes: response.data.results[0].data[idx].row[0].genotypes
                })
            }
*/

            return response.data;
        }
    }

}

export default TableDataService;