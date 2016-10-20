class MenuListController {
    
    /** Costruttore
     * 
     * @param $log
     */
    constructor($log) {
        this.$log = $log;
    }

    selectedVoice() {
        var selected = this.selected;
        
        this.$log.debug(selected.name + ' clicked!');
    }
}

export default MenuListController;