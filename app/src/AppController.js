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
