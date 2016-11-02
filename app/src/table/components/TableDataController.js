class TableDataController {
    
    /** Costruttore
     * 
     * @param $log
     */
    constructor($http, $log, $mdDialog, TableDataService) {
        var self = this;
        self.$log = $log;
   
        self.selected = [];

        self.vcf_headers = {
            'CHROM': 'CHROM',
            'POS':   'POS',
            'ID':    'ID',
            'REF':   'REF',
            'ALT':   'ALT',
            'QUAL':  'QUAL',
            'FILTER': 'FILTER',
            'INFO': 'INFO',
            'GENOTYPES': 'GENOTYPES'
        };
 
        self.query = {
            'limit': 5,
            'page': 1,
            'skip': 0
        };


        self.promise = TableDataService.loadVariantsFromQuery(self.query).then(function(data) {
            console.log(data);
            self.data = data;


        }).catch(function() { console.log('Some error occurred') });

        self.getElems = function () {
            console.log('Getting elements');
            self.query.skip = self.query.limit * (self.query.page - 1);

            self.promise = TableDataService.loadVariantsFromQuery(self.query).then(function(data) {
                console.log(data);
                self.data = data;

            }).catch(function() { console.log('Some error occurred') });
        }

        // Metodo chiamato per visualizzare le annotazioni di una particolare variante
        self.showAnnotations = function($event, annotations){
            self.annotations = annotations;

            var annotationDialog = {
                title: 'Annotations for selected Variant',
                fullscreen: true,
                autowrap: false,
                parent: angular.element(document.body),
                targetEvent: $event,
                templateUrl: './src/table/components/AnnotationDialog.html',
                clickOutsideToClose: true,
                controller: () => self,
                controllerAs: '$ctrl'
            }
            
            $mdDialog.show(annotationDialog)
                .finally(function(){
                    console.log("BUBBU'");
                    self.annotations = null;
                })
        }

        self.closeDialog = function() {
            $mdDialog.hide();
        }
    }

}

export default TableDataController;