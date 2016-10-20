
function TableDataService($q, $http, $resource, $log) {
   
    var data = null;
    return {

        loadData: function(filepath) {
            console.log('Running this function');

            //data = $resource('../../../api/file_queue/test_vcf.json');
            /*
            $http.get(filepath)
               .then(function(response){
                   console.log(response.data);
                   data = response.data;
               })
                .catch(function (error) {
                    $log.error('Failed to load data from JSON file: ' + error.data);
                });
            */
        },
        passData: function() {
            return $q.when(data);
        }

    }
}

export default ['$q', '$http', '$resource', '$log', TableDataService ];

/*
class TableDataService {
    constructor($resource) {
        self.resource = $resource('../../../api/file_queue/test_vcf.json');
    }
}

import angular from 'angular';

angular.module("table").factory('$dataTable', ['$resource', function($resource) {
    console.log("Getting table data...")
    return $resource('../../../api/file_queue/test_vcf.json');
}]);
*/