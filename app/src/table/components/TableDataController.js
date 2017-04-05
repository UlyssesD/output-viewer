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
        self.isArray = angular.isArray;
        //self.show_header = null;
        self.selected = null;
        self.selectedIndex = 0;
        self.config = {};
        self.rows = [];

        self.query = {
            'username': 'lola',
            'experiment': $routeParams.experiment,
            'file': $routeParams.filename,
            'limit': 10,
            'page': 1,
            'first': 1,
            'last': 1,
            'skip': 0,
            'filters': null
        };

        self.hits = null;

        self.filters = null;
        self.previous = [];
        self.limit = 10;

        console.log($routeParams);

        self.config = config;

        self.promise = TableDataService.loadVariantsFromQuery(self.query).then(function(data) {
            self.processDataForVisualization(data);
            self.show_header = data.show_header;
            
            console.log("RETRIEVING COUNT OF HITS...")
            self.query.first = data.first;
            
            TableDataService.getCount(self.query).then(function(data){
                console.log("HIT COUNT RETRIEVED")
                self.hits =data.count;
            })

        }).catch(function () { console.log('Some error occurred') });

        self.getElems = function (type) {

            console.log('Getting elements');

            switch(type){
                case "next":
                    self.previous.push(self.data.first);
                    self.query.last = self.data.last;
                    break;
                case "back":
                    self.query.last = self.previous.pop();

                    break;
                case "limit":
                    self.query.last = self.previous.length != 0 ? self.previous.pop(): self.data.first;
                    break;
            }   
            console.log("Previous = [" + self.previous + "]")
            console.log('Last=' + self.query.last)
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

        self.updateFilters = function (removed_filter) {
            console.log("UPDATING ROWS AFTER REMOVAL OF FILTER");
            console.log(removed_filter);
            
            var idx;
            for (idx in self.filters.list) {

                if ( (self.filters.list[idx].label == removed_filter.name) ) {
                    self.filters.list[idx][removed_filter.var] = null;

                    console.log(self.filters.list[idx]);
                    break;
                }
            }

            self.filterTable();
        }

        self.filterTable = function () {
            console.log("FILTER SUBMISSION TO SERVER");
            self.query.last = 1;
            self.hits = null;
            self.previous = []

            self.query.filters = (JSON.parse(JSON.stringify(self.filters)))

            var idx
            for (idx in self.query.filters.list) {

                if (  self.query.filters.list[idx].type == "select" ) {
                    delete self.query.filters.list[idx]["options"]
                }
                else if (  self.query.filters.list[idx].type == "autocomplete" ) {
                    delete self.query.filters.list[idx]["url"]
                }
            }
            
            

            console.log(self.query.filters)
            self.promise = TableDataService.loadVariantsFromQuery(self.query).then(function(data) {
                self.processDataForVisualization(data);

                console.log("RETRIEVING COUNT OF HITS...")
                self.query.first = data.first;
                TableDataService.getCount(self.query).then(function(data){
                    console.log("HIT COUNT RETRIEVED")
                    self.hits =data.count;
                })

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
            

            //return formElement.options.filter(self.createFilterFor(searchText))
            
            return $http({
                method: 'POST',
                url: formElement.url,
                headers: {
                    'Content-Type': 'Application/json',
                    'Accepts': 'Application/json',
                    'X-Stream': 'true'
                },
                data: {
                    "username": self.query.username,
                    "experiment": self.query.experiment,
                    "file": self.query.file,
                    "term": searchText
                }

            }).then(function(response) {
                console.log("ENTRIES FOR SUBMITTED TERM:");
                console.log(response.data.options);
                return response.data.options
            })
            
        }

        self.createFilterFor = function (query) {
            var lowercaseQuery = angular.lowercase(query);

            return function filterFn(elem) {
                var lowercaseElem = angular.lowercase(elem)
                return (lowercaseElem.indexOf(lowercaseQuery) === 0);
            };

        }

        self.openDialog = function ($event, context) {
            var url = "";
            
            switch (context) {
                case "filters":
                    url = "./src/table/templates/filters.html";
                    if (self.filters == null) {
                        $http.get("http://" + generalConfig.django.address + ":" + generalConfig.django.port + "/dataService/" + self.query.username + "/" + self.query.experiment + "/" + self.query.file + "/filters/")
                        .then(function(response) {
                            console.log("FILTERS RETRIEVED");
                            self.filters = response.data;
                            console.log(self.filters)

                        })
                    }
                    break;
            }

            var dialog = {
                fullscreen: true,
                autowrap: false,
                parent: angular.element(document.body),
                targetEvent: $event,
                templateUrl: url,
                clickOutsideToClose: true,
                controller: () => self,
                controllerAs: '$ctrl'
            }

            $mdDialog.show(dialog)
                .finally(function () {
                    console.log("Dialog closed.");
                    //self.selected = null;
                    //self.genotype_headers = null;
                    //self.displayed_samples = null;
                    //self.genotypes_page = 1;
                })
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

        self.closeDialog = function (context) {

            switch (context) {
                case "filters":
                    self.filterTable();
                    break;
            }

            $mdDialog.hide();
        };
    }

}

export default TableDataController;