import TableDataController from './TableDataController';

export default {
    name : 'tableData',
    config : {
        bindings: {data: '<'},
        templateUrl: 'src/table/components/TableData.html',
        controller: ['$http', '$log', '$resource', TableDataController ]
    }
};