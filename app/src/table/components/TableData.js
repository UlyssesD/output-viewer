import TableDataController from './TableDataController';
import TableDataService from './../services/TableDataService';

export default {
    name : 'tableData',
    config : {
        bindings: {data: '<'},
        templateUrl: 'src/table/components/TableData.html',
        controller: ['$http', '$routeParams', '$log', '$mdDialog', 'TableDataService', TableDataController ]
    }
};