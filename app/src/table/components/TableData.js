import TableDataController from './TableDataController';
import TableDataService from './../services/TableDataService';

export default {
    name : 'tableData',
    config : {
        bindings: {data: '<'},
        templateUrl: 'src/table/components/TableData.html',
        controller: ['$http', '$log', '$mdDialog', 'TableDataService', TableDataController ]
    }
};