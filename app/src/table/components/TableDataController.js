import config from "src/table/config/vcf.config.json!json";
import generalConfig from "configuration.json!json";

class TableDataController {

    /** Costruttore
     * 
     * @param $log
     */
    constructor($http, $routeParams, $log, $mdDialog, TableDataService) {
        var self = this;
        self.$log = $log;

        self.selected = [];
        self.selectedIndex = 0;
        self.config = {};
        self.rows = [];

        self.query = {
            'username': 'lola',
            'experiment': $routeParams.experiment,
            'file': $routeParams.filename,
            'limit': 5,
            'page': 1,
            'skip': 0,
            'filters': null
        };

        self.filters = null;


        console.log($routeParams);

        self.config = config;

        $http.get("http://" + generalConfig.django.address + ":" + generalConfig.django.port + "/dataService/" + self.query.username + "/" + self.query.experiment + "/" + self.query.file + "/filters/")
            .then(function(response) {
                console.log("FILTERS RETRIEVED");
                self.filters = response.data;
                console.log(self.filters)
            })

        self.promise = TableDataService.loadVariantsFromQuery(self.query).then(function(data) {
            self.processDataForVisualization(data);
        }).catch(function () { console.log('Some error occurred') });

        self.getElems = function () {
            console.log('Getting elements');
            self.query.skip = self.query.limit * (self.query.page - 1);

            self.promise = TableDataService.loadVariantsFromQuery(self.query).then(function(data) {
            self.processDataForVisualization(data);
        }).catch(function () { console.log('Some error occurred') });
        };

        self.processDataForVisualization = function(data) {
            self.data = data;

            //self.template = self.config.row.join("\n");
            

/*
            for( var i = 0; i < data.variants.length; i++) {
                self.rows.push({
                    "data": self.data.variants[i],
                    "row": $interpolate(template)(self.data.variants[i])
                });
            }
*/
            console.log(self.data)

        }

        self.getSamples = function () {
            self.displayed_samples = self.selected.genotypes.slice(5 * (self.genotypes_page - 1), Math.min(self.selected.genotypes.length, 5 * (self.genotypes_page - 1) + 5));
            console.log("Showing more samples");
            console.log(self.displayed_samples);
        };

        self.filterTable = function () {
            console.log("FILTER SUBMISSION TO SERVER");
            self.query.filters = self.filters

            self.promise = TableDataService.loadVariantsFromQuery(self.query).then(function(data) {
                self.processDataForVisualization(data);
            }).catch(function () { console.log('Some error occurred') });

        }

        // ---- Funzione che riceve da server i dati da visualizzare nel form corrente
        self.fetchFields = function(formElement) {
            
            if (!formElement.options) {

                return $http.get(formElement.url)
                    .then(function(response) {
                        console.log("Options for field " + formElement.label + " -- RETRIEVED");
                        console.log(response.data);
                        
                        formElement.options = response.data.elements;
                    })

            }    
        }

        self.searchTerm = function(searchText, formElement) {
            
            return $http.get(formElement.url + "?q=" + searchText)
                .then(function(response) {
                    console.log("Matches for search term " + searchText + " -- RETRIEVED")
                    console.log(response.data);

                    return response.data.elements
                })
        }

        self.createFilterFor = function (query) {
            var lowercaseQuery = angular.lowercase(query);

            return function filterFn(elem) {
                var lowercaseElem = angular.lowercase(elem)
                return (lowercaseElem.indexOf(lowercaseQuery) === 0);
            };

        }

        // Metodo chiamato per visualizzare le annotazioni di una particolare variante
        self.showAnnotations = function ($event, selected) {

            self.selected = selected;
            self.genotype_headers = selected.variant.attr.FORMAT.split(':');
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