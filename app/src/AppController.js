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
    self.upload = function (file) {
        console.log(file);
/*       
        var reader = new FileReader();
        reader.onload = function(event) {
            var contents = event.target.result;
            console.log("File contents: " + contents);
            
            
        };
        
        reader.onerror = function(event) {
        console.error("File could not be read! Code " + event.target.error.code);
        };

        reader.readAsText(file);
*/

        Upload.upload({
                url: 'api/upload.php',
                method: 'POST',
                file: file,
                headers: {'Content-Type': 'text'},
                data: {'targetPath': 'file_queue/'}
        }).then(function (resp) {
            console.log('Success! Response: ' + resp.data );
        }, function (resp) {
            console.log('Error status: ' + resp.status);
        }, function (evt) {
            var progressPercentage = parseInt(100.0 * evt.loaded / evt.total);
            console.log('progress: ' + progressPercentage + '% ');
        });

/*
 Upload.upload({
            url: 'upload.php',
            method: 'GET',
            headers: {
                'Authorization': 'xxx'
            },
            data: {
              target_path: '/upload/',
              file: file
            }
        });

*/
    };

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
