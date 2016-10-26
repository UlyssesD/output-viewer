class TableDataController {
    
    /** Costruttore
     * 
     * @param $log
     */
    constructor($http, $log, $resource, TableDataService) {
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

        this.getElems = function () {
            console.log('Getting elements');
            self.query.skip = self.query.limit * (self.query.page - 1);

            self.promise = TableDataService.loadVariantsFromQuery(self.query).then(function(data) {
                console.log(data);
                self.data = data;

            }).catch(function() { console.log('Some error occurred') });
        }
    }

}

export default TableDataController;