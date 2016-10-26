class TableDataService {

        constructor($q, $http, $log) {
        var self = this;

        // Attributi della classe (da Angular)
        self.$q = $q;
        self.$http = $http;
        self.$log = $log;

        // Attributi della classe SPECIFICI
        self.credentials = btoa('neo4j:password');

        // --- Metodi pubblici della classe ---

        // Interrogo il database per ottenere le varianti secondo la query passata in input
        self.loadVariantsFromQuery = function ( query ) {
            console.log('Retrieving data for selected query...');

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
                    "statements" : [
                        {
                            "statement":  "match(v: Variant),(f: File) where exists((f)-[:Contains]->(v)) and f.name='test_vcf' with count(v) as total match(f: File)-[:Contains]->(v: Variant) where f.name = 'test_vcf' with total, v as variant order by ID(v) skip {skip} limit {limit} match (g: Genotype) where exists((variant)-[:Sample]->(g: Genotype)) with total, variant, collect(g) as genotype_list, count(g) as genotypes match (variant)-[:Annotation]->(i: Info) return {total: total, variant: variant, genotypes: genotype_list, annotations: i}",
                            "parameters": {
                                "skip": query.skip,
                                "limit": query.limit
                            }
                        }

                    ]
                }
            }).then(self.variantRetrieved);
        };

        // Metodo chiamato una volta ottenute le varianti dal Database. Riorganizzo i dati prima di passarli alla vista
        self.variantRetrieved = function(response) {
            console.log('Data successfully retrieved');

            var data = {
                count: 0,
                variants: []
            };

            data.count = response.data.results[0].data[0].row[0].total;

            for (var idx = 0; idx < response.data.results[0].data.length; idx++) {
            
                data.variants.push({
                    variant: response.data.results[0].data[idx].row[0].variant,
                    annotations: response.data.results[0].data[idx].row[0].annotations,
                    genotypes:response.data.results[0].data[idx].row[0].genotypes
                })
            }

            return data;
        }
    }

}

export default TableDataService;