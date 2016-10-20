import MenuListController from './MenuListController'

export default {
    name : 'menuList',
    config : {
        bindings: {menuItems: '<', selected: '<', selectItem: '&onSelected'},
        templateUrl: 'src/menu/components/list/MenuList.html',
        controller: ['$log', MenuListController]
    }
};