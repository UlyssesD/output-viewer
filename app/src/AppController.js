/**
 * Main App Controller for the Angular Material Starter App
 * @param MenuDataService
 * @param $mdSidenav
 * @constructor
 */

function AppController( MenuDataService, TableDataService, Upload, $mdSidenav) {
    var self = this;
    //self.data         = null;

    self.openStatistics   = openStatistics;

/*
    TableDataService.loadVariantsFromQuery({
            'limit': 5,
            'page': 1,
            'skip': 0
        }).then(function(data){ console.log('trallallero'); console.log(data)});
*/
    

    console.log(self.data);
/*
    TableDataService.loadData('api/file_queue/test_vcf.json');
    TableDataService
        .passData()
        .then( function (items)  {
            self.data = items;
            
            console.log(self.data);
        });

*/   
    // *********************************
    // Internal methods
    // *********************************

    /**
     * Hide or Show the 'left' sideNav area
     */
    function openStatistics() {
        $mdSidenav('right').toggle();
    }

}
export default ['MenuDataService', 'TableDataService', 'Upload', '$mdSidenav', AppController ];
