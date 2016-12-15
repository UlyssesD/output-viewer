import menuItems from "src/menu/config/output_viewer.config.json!json";

class MenuListController {

    /** Costruttore
     * 
     * @param $log
     */
    constructor($log, $http) {
        var self = this

        self.$log = $log;
        self.menuItems = {};
        self.selected = null;

        self.menuItems = menuItems;

        self.selectItem = function (item) {
            self.selected = item.name;

            console.log(self.selected + ' clicked!');
        }
    }

}

export default MenuListController;