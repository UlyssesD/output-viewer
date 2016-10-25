class TableDataController {
    
    /** Costruttore
     * 
     * @param $log
     */
    constructor($http, $log, $resource) {
        var self = this;
        self.$log = $log;
        self.$http = $http;
        //self.resource = $resource('http://localhost:28017/test_vcf/rows/\\:id');


        var credentials = btoa('neo4j:password');
        //$http.defaults.headers.common['Authorization'] = 'Basic ' + credentials;
        //$http.defaults.header.common['Content-type'] = 'application/json';
        
         self.query = {
            'limit': 20,
            'page': 1,
            'skip': 0
        };

        self.success = function(elems) {
            console.log("Data retrieved, loading data in view...");
            self.data = elems.data.results[0].data;
            self.count = elems.data.results[0].data[0].row[0].total;
            console.log(self.data);
        }


        // Ottengo la riga di header per le varianti
        $http({
            method: 'POST',
            url: 'http://localhost:7474/db/data/transaction/commit',
            headers: {
                'Authorization': 'Basic ' + credentials,
                'Content-Type': 'Application/json',
                'Accepts': 'Application/json'
            },
            data: {
                "statements" : [
                    {
                        "statement": "match (v: Variant) return {headers: keys(v)} limit 1"
                    }
                ]
            }
        }).then(function(elems){
            console.log(elems);
            self.headers = elems.data.results[0].data[0].row[0].headers;
        }, null);

        self.promise = $http({
            method: 'POST',
            url: 'http://localhost:7474/db/data/transaction/commit',
            headers: {
                'Authorization': 'Basic ' + credentials,
                'Content-Type': 'Application/json',
                'Accepts': 'Application/json',
                'X-Stream': 'true'
            },
            data: {
                "statements" : [
                    {
                        "statement":  "match(v: Variant),(f: File) where exists((f)-[:Contains]->(v)) and f.name='test_vcf' with count(v) as total match(f: File)-[:Contains]->(v: Variant) where f.name = 'test_vcf' with total, v as variant order by ID(v) skip {skip} limit {limit} match (g: Genotype) where exists((variant)-[:Sample]->(g: Genotype)) with total, variant, collect(g) as genotype_list, count(g) as genotypes match (variant)-[:Annotation]->(i: Info) return {total: total, variant: variant, genotypes: genotype_list, annotations: i}",
                        "parameters": {
                            "skip": self.query.skip,
                            "limit": self.query.limit
                        }
                    }

                ]
            }
        }).then(self.success, function(){console.log('Some error occurred.');}).$promise;
        
        //this.$dataTable = $dataTable;
/*
        $http.get('api/file_queue/test_vcf.json').then(function(response) {
        self.data = response.data;

        console.log(self.data);
      });
*/

        //self.$http.get('http://127.0.0.1:28017/test_vcf/rows/?limit=' + self.query.limit + '&page=' + self.query.page).then(self.success, null).$promise;
        //self.promise = self.resource.get(self.query, self.success).$promise;

        this.getElems = function () {
            console.log('Getting elements');
            self.query.skip = self.query.limit * (self.query.page - 1);

            self.promise = $http({
            method: 'POST',
            url: 'http://localhost:7474/db/data/transaction/commit',
            headers: {
                'Authorization': 'Basic ' + credentials,
                'Content-Type': 'Application/json',
                'Accepts': 'Application/json'
            },
            data: {
                "statements" : [
                    {
                        "statement":  "match(v: Variant),(f: File) where exists((f)-[:Contains]->(v)) and f.name='test_vcf' with count(v) as total match(f: File)-[:Contains]->(v: Variant) where f.name = 'test_vcf' with total, v as variant order by ID(v) skip {skip} limit {limit} match (g: Genotype) where exists((variant)-[:Sample]->(g: Genotype)) with total, variant, collect(g) as genotype_list, count(g) as genotypes match (variant)-[:Annotation]->(i: Info) return {total: total, variant: variant, genotypes: genotype_list, annotations: i}",
                        "parameters": {
                            "skip": self.query.skip,
                            "limit": self.query.limit
                        }
                    }

                ]
            }
            }).then(self.success, function(){console.log('Some error occurred.');}).$promise;

            //self.promise = self.resource.get(self.query, self.success).$promise;
        }
    }

}

export default TableDataController;