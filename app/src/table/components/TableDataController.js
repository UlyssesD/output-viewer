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
            'POS': 'POS',
            'ID': 'ID',
            'REF': 'REF',
            'ALT': 'ALT',
            'QUAL': 'QUAL',
            'FILTER': 'FILTER',
            'INFO': 'INFO',
            'GENOTYPES': 'GENOTYPES'
        };

        self.query = {
            'file': 'U11_80M_R2.annotated.hg19_multianno.vcf',
            'limit': 5,
            'page': 1,
            'skip': 0
        };

        TableDataService.loadFileStatistics(self.query).then(function(data) {
            console.log(data);
            self.statistics = data;

        }).catch(function () { console.log('Some error occurred') });

        self.promise = TableDataService.loadVariantsFromQuery(self.query).then(function (data) {
            console.log(data);
            self.data = data;


        }).catch(function () { console.log('Some error occurred') });

        self.getElems = function () {
            console.log('Getting elements');
            self.query.skip = self.query.limit * (self.query.page - 1);

            self.promise = TableDataService.loadVariantsFromQuery(self.query).then(function (data) {
                console.log(data);
                self.data = data;

            }).catch(function () { console.log('Some error occurred') });
        };

        self.getSamples = function () {
            self.displayed_samples = self.selected.genotypes.slice(5 * (self.genotypes_page - 1), Math.min(self.selected.genotypes.length, 5 * (self.genotypes_page - 1) + 5));
            console.log("Showing more samples");
            console.log(self.displayed_samples);
        };

        // Metodo chiamato per visualizzare le annotazioni di una particolare variante
        self.showAnnotations = function ($event, selected) {

            self.selected = selected;
            self.genotype_headers = selected.variant.FORMAT.split(':');
            self.genotypes_page = 1;
            self.displayed_samples = self.selected.genotypes.slice(5 * (self.genotypes_page - 1), Math.min(self.selected.genotypes.length, 5 * (self.genotypes_page - 1) + 5));

            var annotationDialog = {
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
                .finally(function () {
                    console.log("Dialog closed.");
                    self.selected = null;
                    self.genotype_headers = null;
                    self.displayed_samples = null;
                    self.genotypes_page = 1;
                })
        };

        self.closeDialog = function () {
            $mdDialog.hide();
        };
    }

}

export default TableDataController;