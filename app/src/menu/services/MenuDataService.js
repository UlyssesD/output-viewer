/** MenuDataService
 *  Modello di dati sviluppato a mano per la gestione delle varie voci del menu principale
 * 
 * @returns {{LoadAll: Function}}
 * @constructor
 */

function MenuDataService($q) {
    var menuItems = [
        {
            name: 'Item One'
        },
        {
            name: 'Item Two'
        },
        {
            name: 'Item Three'
        },
        {
            name: 'Item Four'
        }
    ];

    return {
        loadAllItems: function () {
            return $q.when(menuItems);
        }
    };
}

export default ['$q', MenuDataService];