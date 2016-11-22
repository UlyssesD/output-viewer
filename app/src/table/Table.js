import TableDataService from 'src/table/services/TableDataService';

import TableData from 'src/table/components/TableData';


// Definizione del modulo Angular 'Table'

export default angular
    .module("table", ['ngMaterial', 'angular-bind-html-compile', 'md.data.table'])

    .component(TableData.name, TableData.config)
    
    .service("TableDataService", TableDataService);

