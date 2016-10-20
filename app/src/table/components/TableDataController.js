class TableDataController {
    
    /** Costruttore
     * 
     * @param $log
     */
    constructor($http, $log, $resource) {
        var self = this;
        self.$log = $log;
        self.$http = $http;
        self.resource = $resource('http://localhost:28017/test_vcf/rows/\\:id');

        //this.$dataTable = $dataTable;
/*
        $http.get('api/file_queue/test_vcf.json').then(function(response) {
        self.data = response.data;

        console.log(self.data);
      });
*/
        self.query = {
            'sort': {"_id": 1},
            'limit': 20,
            'page': 1,
            'skip': 0
        };

        self.success = function(elems) {
            console.log("Data retrieved, loading data in view...");
            self.data = elems.rows;
            console.log(self.data);

        }

        //self.$http.get('http://127.0.0.1:28017/test_vcf/rows/?limit=' + self.query.limit + '&page=' + self.query.page).then(self.success, null).$promise;
        self.promise = self.resource.get(self.query, self.success).$promise;

        this.getElems = function () {
            console.log('Getting elements');
            self.query.skip = self.query.limit * (self.query.page - 1);
            self.promise = self.resource.get(self.query, self.success).$promise;
        }
    }

}

export default TableDataController;